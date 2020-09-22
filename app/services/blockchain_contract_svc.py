from databases import Database
from sqlalchemy.sql import select

from ..db import (blockchain_contracts, parties)
from .base_svc import BaseService
from ..schemas import (UserInDb, BlockchainContractCreate)


class BlockchainContractService(BaseService):
    async def create(
            self,
            db: Database, user: UserInDb,
            obj: BlockchainContractCreate
    ):
        obj_data = self._to_dict(obj)
        await self._uid_to_fk(db, obj_data, parties, 'owner')
        return await self._insert(db, obj_data)

    def _select_query(self):
        return select([
            blockchain_contracts.c.uid,
            blockchain_contracts.c.name,
            blockchain_contracts.c.contract_address,
            blockchain_contracts.c.contract_code,
            blockchain_contracts.c.contract_abi,
            parties.c.uid.label('owner_uid')
        ]).select_from(blockchain_contracts.join(parties))


blockchain_contract_service = BlockchainContractService(blockchain_contracts)
