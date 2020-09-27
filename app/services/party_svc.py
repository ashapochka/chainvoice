from uuid import UUID

from fastapi import (Depends, BackgroundTasks)
from loguru import logger
from databases import Database
from eth_account import Account
from eth_account.account import LocalAccount

from ..blockchain import get_erc1155_contract
from ..db import parties, get_db
from .base_svc import BaseService
from ..schemas import (
    UserInDb, PartyCreate, PartyTokenBalance, PartyTokenTransfer,
    PartyTokenTransferReceipt, UID, PartyGet
)
from .secret_cvs import secret_service
from ..contracts import ERC1155Contract
from ..config import get_settings
from .utils import raise_not_found_if_none, raise_not_found


# noinspection SpellCheckingInspection
class PartyService(BaseService):
    def __init__(
            self,
            db: Database = Depends(get_db),
            background_tasks: BackgroundTasks = None,
            token_contract: ERC1155Contract = Depends(get_erc1155_contract)
    ):
        super().__init__(parties, db)
        self.background_tasks = background_tasks
        self.token_contract = token_contract

    async def create(
            self, user: UserInDb,
            obj: PartyCreate,
            create_blockchain_account: bool = True,
            token_id: int = 0,
            initial_amount: int = 1_000_000_00,
            token_owner: LocalAccount = None
    ):
        account = None
        if create_blockchain_account:
            account = Account.create()
        elif obj.blockchain_account_key is not None:
            # noinspection PyCallByClass
            account = Account.from_key(
                obj.blockchain_account_key.get_secret_value()
            )
        if account is not None:
            obj.blockchain_account_address = account.address
            self.save_blockchain_account(account)
        obj_data = self._to_dict(obj)
        obj_data.pop('blockchain_account_key', '')
        result = await self._insert(obj_data)
        if initial_amount > 0 and obj.blockchain_account_address is not None:
            if token_owner is None:
                qadmin_name = get_settings().qadmin_name
                qadmin = await self.get_one_by_name(user, qadmin_name)
                raise_not_found_if_none(
                    qadmin, 'party', qadmin_name,
                    msg='quorum admin party expected to always exist'
                )
                token_owner = self.get_party_account(qadmin)

            def _transfer_tokens():
                self.token_contract.safe_transfer_from(
                    signer=token_owner,
                    from_address=token_owner.address,
                    to_address=obj.blockchain_account_address,
                    token_id=token_id,
                    amount=initial_amount,
                    data=b'initial amount transfer'
                )
            # when calling from request, execute on the background,
            # else execute as part of the same flow
            if self.background_tasks is not None:
                self.background_tasks.add_task(_transfer_tokens)
            else:
                _transfer_tokens()
        return result

    @staticmethod
    def get_party_address(party_record) -> str:
        account_address = party_record['blockchain_account_address']
        if not account_address:
            raise_not_found('party account address', party_record['uid'])
        return account_address

    @staticmethod
    def get_party_account(party_record) -> LocalAccount:
        account_address = PartyService.get_party_address(party_record)
        account_key = secret_service.get_secret_value(account_address)
        account = Account.from_key(account_key)
        return account

    @staticmethod
    def save_blockchain_account(account: LocalAccount):
        name = account.address
        value = account.key.hex()
        secret_service.set_secret(
            name, value,
            content_type='quorum_account',
            tags={'owner': 'chainvoice'}
        )

    async def create_qadmin_party(self, user: UserInDb) -> PartyGet:
        settings = get_settings()
        async with self.db.transaction():
            qadmin = await self.get_one_by_name(user, settings.qadmin_name)
            if not qadmin:
                await self.create(
                    user,
                    PartyCreate(
                        name=settings.qadmin_name,
                        blockchain_account_address=settings.qadmin_address,
                        blockchain_account_key=settings.qadmin_private_key
                    ),
                    create_blockchain_account=False, initial_amount=0
                )
            qadmin = await self.get_one_by_name(user, settings.qadmin_name)
            return PartyGet(**qadmin)

    async def get_token_balance(
        self, user: UserInDb,
        uid: UUID, token_id: int = 0
    ) -> PartyTokenBalance:
        party_record = await self.get_one_by_uid(
            user, uid, raise_not_found=True, what='party'
        )
        address = party_record['blockchain_account_address']
        if not address:
            token_amount = 0
        else:
            token_amount = self.token_contract.balance_of(address, token_id)
        return PartyTokenBalance(
            token_amount=token_amount,
            token_id=token_id,
            **party_record
        )

    async def transfer_tokens(
            self, user: UserInDb,
            uid: UUID, obj: PartyTokenTransfer
    ) -> PartyTokenTransferReceipt:
        from_record = await self.get_one_by_uid(
            user, uid, raise_not_found=True, what='party'
        )
        from_account = self.get_party_account(from_record)
        to_record = await self.get_one_by_uid(
            user, UUID(obj.to_uid), raise_not_found=True, what='party'
        )
        to_address = self.get_party_address(to_record)
        txn_receipt = self.token_contract.safe_transfer_from(
            from_account, from_account.address, to_address,
            obj.token_id, obj.token_amount, obj.data
        )
        txn_hash = txn_receipt.transactionHash.hex()
        logger.debug(f'transfer txn hash: {txn_hash}')
        txn_input = self.token_contract.decode_tx_input(txn_hash)
        logger.debug(f'txn input: {txn_input}')
        return PartyTokenTransferReceipt(
            **obj.dict(), txn_hash=txn_hash,
            from_uid=UID(uid), from_address=from_account.address,
            to_address=to_address
        )

