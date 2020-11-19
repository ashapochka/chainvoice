from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from .base_api import BaseAPI
from ..schemas import (
    TransactionGet,
)
from ..services import LedgerStateService

router = InferringRouter()


# noinspection PyTypeChecker
@cbv(router)
class LedgerStateAPI(BaseAPI):
    service: LedgerStateService = Depends()

    @router.get('/tx/paid/')
    async def get_paid_transactions(
            self, offset: int = 0, limit: int = 20
    ) -> List[TransactionGet]:
        return await self._get_many(
            limit, offset
        )
