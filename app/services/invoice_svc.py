import time
from datetime import date, timedelta
from uuid import uuid4, UUID

from databases import Database
from eth_account import Account
from fastapi import Depends
from sqlalchemy.sql import select
from loguru import logger

from .order_svc import OrderService
from .order_item_svc import OrderItemService
from .party_svc import PartyService
from .secret_cvs import secret_service
from .utils import raise_forbidden, money_to_token
from ..blockchain import get_invoice_registry_contract
from ..contracts import InvoiceRegistryContract
from ..contracts.utils import check_tx_success, uuid_to_hex
from ..db import (invoices, orders, get_db)
from ..schemas import (InvoiceCreate, UserInDb, InvoiceUpdate, InvoiceState)
from .base_svc import BaseService


class InvoiceService(BaseService):
    def __init__(
            self,
            db: Database = Depends(get_db),
            order_service: OrderService = Depends(),
            order_item_service: OrderItemService = Depends(),
            party_service: PartyService = Depends(),
            invoice_registry_contract: InvoiceRegistryContract = Depends(
                get_invoice_registry_contract
            )
    ):
        super().__init__(invoices, db)
        self.order_service = order_service
        self.order_item_service = order_item_service
        self.party_service = party_service
        self.invoice_registry_contract = invoice_registry_contract

    async def create(
            self, user: UserInDb, obj: InvoiceCreate,
            token_id: int = 0,
    ):
        await self._check_for_active_invoices(user, obj.order_uid)
        obj_data = obj.dict(exclude_unset=True)
        invoice_uid = uuid4()
        obj_data['uid'] = str(invoice_uid)
        obj_data['state'] = 'DRAFT'
        # if obj_data['state'] != 'draft':
        #     raise_forbidden(
        #         msg='new invoice must have draft state',
        #         obj=obj
        #     )
        if not obj.ref_id:
            obj_data['ref_id'] = f"INV-{int(time.time())}-{obj_data['uid'][:4]}"
        if not obj.due_date:
            obj_data['due_date'] = date.today() + timedelta(weeks=2)
            # TODO: make timedelta configurable
        elif obj.due_date < date.today():
            raise_forbidden(
                msg=f'invoice due date must be >= {date.today()}',
                obj=obj
            )
        await self._uid_to_fk(obj_data, orders, 'order')
        order = await self._get_order(user, obj.order_uid)
        seller_account = await self._get_seller_account(
            user, order['seller_uid']
        )
        buyer = await self.party_service.get_one_by_uid(
            user, order['customer_uid'], raise_not_found=True
        )
        buyer_address = buyer['blockchain_account_address']
        # TODO: check address exists
        order_items = await self.order_item_service.get_many(
            user, 0, 1000, order_uid=str(obj.order_uid)
        )
        # TODO: what if there are more than 1000 items?
        # TODO: do we allow invoice for the order with 0 items?
        total_amount = sum(
            item['base_price'] * item['quantity'] for item in order_items
        )
        blockchain_invoice_id = uuid_to_hex(invoice_uid)
        tx_receipt = self.invoice_registry_contract.register_invoice(
            seller_account=seller_account,
            invoice_id=blockchain_invoice_id,
            buyer_address=buyer_address,
            token_id=token_id,
            amount=money_to_token(total_amount)
        )
        self._check_invoice_tx(blockchain_invoice_id, tx_receipt)
        return await self._insert(obj_data)

    def _check_invoice_tx(self, blockchain_invoice_id, tx_receipt):
        logger.debug(tx_receipt)
        check_tx_success(tx_receipt, raise_on_failure=True)
        logger.debug(self.invoice_registry_contract.get_invoice(
            blockchain_invoice_id
        ))

    async def _check_for_active_invoices(self, user, order_uid):
        existing_invoices = await self.get_many(
            user, 0, 1000, order_uid=str(order_uid)
        )
        order_has_active_invoices = any(
            inv['state'] != 'CANCELED' for inv in existing_invoices
        )
        if order_has_active_invoices:
            raise_forbidden(
                msg='cannot create new invoice: '
                    'order already has active invoices',
                order_uid=order_uid
            )

    async def _get_order(self, user, order_uid):
        order = await self.order_service.get_one_by_uid(
            user, order_uid, raise_not_found=True
        )
        return order

    async def _get_seller_account(self, user, seller_uid):
        seller = await self.party_service.get_one_by_uid(
            user, seller_uid, raise_not_found=True
        )
        seller_address = seller['blockchain_account_address']
        # TODO: check address exists
        seller_key = secret_service.get_secret_value(seller_address)
        # TODO: check key exists
        seller_account = Account.from_key(seller_key)
        return seller_account

    def _select_query(self):
        from_query = select([
            invoices.c.uid.label('uid'),
            invoices.c.ref_id.label('ref_id'),
            orders.c.uid.label('order_uid'),
            invoices.c.due_date.label('due_date'),
            invoices.c.state.label('state')
        ]).select_from(
            invoices.join(orders)
        ).alias('from_query')
        query = select(from_query.c).select_from(from_query)
        return query

    async def _change_state(
            self, user: UserInDb, uid: UUID, new_state: InvoiceState
    ):
        invoice = await self.get_one_by_uid(user, uid, raise_not_found=True)
        order = await self._get_order(user, invoice['order_uid'])
        seller_account = await self._get_seller_account(
            user, order['seller_uid']
        )
        blockchain_uid = uuid_to_hex(uid)
        if new_state == InvoiceState.unpaid:
            tx_receipt = self.invoice_registry_contract.publish_invoice(
                seller_account, blockchain_uid
            )
        elif new_state == InvoiceState.canceled:
            tx_receipt = self.invoice_registry_contract.cancel_invoice(
                seller_account, blockchain_uid
            )
        else:
            raise ValueError(f"Change of state to {new_state} not supported")
        self._check_invoice_tx(blockchain_uid, tx_receipt)
        await self.update_by_uid(
            user, uid, InvoiceUpdate(state=new_state)
        )

    async def publish(self, user: UserInDb, uid: UUID):
        await self._change_state(user, uid, InvoiceState.unpaid)

    async def cancel(self, user: UserInDb, uid: UUID):
        await self._change_state(user, uid, InvoiceState.canceled)
