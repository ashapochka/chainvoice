from uuid import UUID

from databases import Database
from fastapi import Depends
from sqlalchemy.sql import select
from loguru import logger

from .party_svc import PartyService
from .invoice_svc import InvoiceService
from .utils import money_to_token, current_time
from ..blockchain import get_erc1155_contract, get_invoice_registry_contract
from ..contracts import ERC1155Contract, InvoiceRegistryContract
from ..contracts.utils import uuid_to_hex, check_tx_success
from ..db import (payments, invoices, get_db, parties, orders)
from ..schemas import (PaymentCreate, UserInDb)
from .base_svc import BaseService


class PaymentService(BaseService):
    def __init__(
            self,
            db: Database = Depends(get_db),
            party_service: PartyService = Depends(),
            invoice_service: InvoiceService = Depends(),
            token_contract: ERC1155Contract = Depends(
                get_erc1155_contract
            ),
            invoice_registry: InvoiceRegistryContract = Depends(
                get_invoice_registry_contract
            )
    ):
        super().__init__(payments, db)
        self.party_service = party_service
        self.invoice_service = invoice_service
        self.token_contract = token_contract
        self.invoice_registry = invoice_registry

    async def create(self, user: UserInDb, obj: PaymentCreate, tx: bool = True):
        obj_data = self._to_dict(obj)
        await self._uid_to_fk(obj_data, invoices, 'invoice')
        customers = parties.alias('customers')
        query = select([
            customers.c.uid.label('uid')
        ]).select_from(
            invoices.join(orders).join(
                customers, orders.c.customer_id == customers.c.id
            )
        ).where(invoices.c.uid == str(obj.invoice_uid))
        buyer = await self.db.fetch_one(query)
        buyer_account = await self.party_service.get_account_by_uid(
            user, buyer['uid'], raise_not_found_=True
        )
        signer = buyer_account
        from_address = buyer_account.address
        to_address = self.invoice_registry.contract.address
        token_id = 0
        token_amount = money_to_token(obj.amount)
        invoice_uid = UUID(obj.invoice_uid)
        blockchain_invoice_id = uuid_to_hex(invoice_uid)
        logger.debug({
            'signer': signer.address,
            'from': from_address,
            'to': to_address,
            'token_id': token_id,
            'token_amount': token_amount,
            'blockchain_invoice_id': blockchain_invoice_id
        })
        tx_receipt = self.token_contract.safe_transfer_from(
            signer, from_address, to_address,
            token_id, token_amount,
            blockchain_invoice_id
        )
        self._check_payment_tx(blockchain_invoice_id, tx_receipt)
        obj_data['blockchain_tx_hash'] = tx_receipt['transactionHash'].hex()
        obj_data['paid_at'] = current_time()
        result = await self._insert(obj_data, tx=tx)
        await self.invoice_service.sync_state_from_blockchain(user, invoice_uid)
        return result

    def _check_payment_tx(self, blockchain_invoice_id, tx_receipt):
        logger.debug(tx_receipt)
        check_tx_success(tx_receipt, raise_on_failure=True)
        logger.debug(self.invoice_registry.get_invoice(
            blockchain_invoice_id
        ))

    def _select_query(self):
        from_query = select([
            payments.c.uid.label('uid'),
            invoices.c.uid.label('invoice_uid'),
            payments.c.amount.label('amount'),
            payments.c.paid_at.label('paid_at'),
            payments.c.blockchain_tx_hash.label('blockchain_tx_hash')
        ]).select_from(
            payments.join(invoices)
        ).alias('from_query')
        query = select(from_query.c).select_from(from_query)
        return query
