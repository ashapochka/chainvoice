from assertpy import assert_that
from databases import Database
from eth_account import Account
from eth_account.account import LocalAccount

from ..db import parties
from .base_svc import BaseService
from ..schemas import (UserInDb, PartyCreate, PartyGet)
from .secret_cvs import secret_service
from ..contracts import ERC1155Contract
from ..config import get_settings


class PartyService(BaseService):

    async def create(
            self, db: Database, user: UserInDb,
            obj: PartyCreate,
            create_blockchain_account: bool = True,
            token_id: int = 0,
            initial_amount: int = 1_000_000_00,
            token_contract: ERC1155Contract = None,
            token_owner: LocalAccount = None
    ):
        account = None
        if create_blockchain_account:
            account = Account.create()
        elif obj.blockchain_account_key is not None:
            account = Account.from_key(obj.blockchain_account_key)
        if account is not None:
            obj.blockchain_account_address = account.address
            self.save_blockchain_account(account)
        obj_data = self._to_dict(obj)
        obj_data.pop('blockchain_account_key', '')
        result = await self._insert(db, obj_data)
        if initial_amount > 0 and obj.blockchain_account_address is not None:
            if token_owner is None:
                qadmin = await self.get_one_by_name(
                    db, user, get_settings().qadmin_name
                )
                assert_that(qadmin).is_not_none()
                qadmin_address = qadmin['blockchain_account_address']
                assert_that(qadmin_address).is_not_none()
                qadmin_key = secret_service.get_secret_value(qadmin_address)
                token_owner = Account.from_key(qadmin_key)
            token_contract.safe_transfer_from(
                signer=token_owner,
                from_address=token_owner.address,
                to_address=obj.blockchain_account_address,
                token_id=token_id,
                amount=initial_amount,
                data=b'initial amount transfer'
            )
        return result

    @staticmethod
    def save_blockchain_account(account: LocalAccount):
        name = account.address
        value = account.key.hex()
        secret_service.set_secret(
            name, value,
            content_type='quorum_account',
            tags={'owner': 'chainvoice'}
        )

    async def create_qadmin_party(self, db: Database, user: UserInDb):
        settings = get_settings()
        async with db.transaction():
            qadmin = await self.get_one_by_name(
                db, user, settings.qadmin_name
            )
            if not qadmin:
                await self.create(
                    db, user,
                    PartyCreate(
                        name=settings.qadmin_name,
                        blockchain_account_address=settings.qadmin_address,
                        blockchain_account_key=settings.qadmin_private_key
                    ),
                    create_blockchain_account=False, initial_amount=0
                )


party_service = PartyService(parties)
