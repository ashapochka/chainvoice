from databases import Database
from fastapi import Depends
from sqlalchemy.sql import select

from ..db import (blockchain_contracts, parties, get_db)
from .base_svc import BaseService
from ..schemas import (UserInDb, BlockchainContractCreate)


class BlockchainContractService(BaseService):
    def __init__(
            self,
            db: Database = Depends(get_db),
    ):
        super().__init__(blockchain_contracts, db)

    async def create(
            self, user: UserInDb, obj: BlockchainContractCreate, tx: bool = True
    ):
        obj_data = self._to_dict(obj)
        await self._uid_to_fk(obj_data, parties, 'owner')
        return await self._insert(obj_data, tx=tx)

    def _select_query(self):
        from_query = select([
            blockchain_contracts.c.uid.label('uid'),
            blockchain_contracts.c.name.label('name'),
            blockchain_contracts.c.contract_address.label('contract_address'),
            blockchain_contracts.c.contract_code.label('contract_code'),
            blockchain_contracts.c.contract_abi.label('contract_abi'),
            parties.c.uid.label('owner_uid').label('owner_uid')
        ]).select_from(blockchain_contracts.join(parties)).alias('from_query')
        query = select(from_query.c).select_from(from_query)
        return query
