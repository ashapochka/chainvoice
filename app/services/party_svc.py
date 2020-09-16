from databases import Database
from eth_account import Account
from eth_account.account import LocalAccount

from ..db import parties
from .base_svc import BaseService
from ..schemas import (UserInDb, PartyCreate)
from .secret_cvs import secret_service


class PartyService(BaseService):

    async def create(self, db: Database, user: UserInDb, obj: PartyCreate):
        if obj.blockchain_account_address is None:
            account = Account.create()
            obj.blockchain_account_address = account.address
            self.save_blockchain_account(account)
        return await super().create(db, user, obj)

    @staticmethod
    def save_blockchain_account(account: LocalAccount):
        name = account.address
        value = account.key.hex()
        secret_service.set_secret(
            name, value,
            content_type='quorum_account',
            tags={'owner': 'chainvoice'}
        )


party_service = PartyService(parties)
