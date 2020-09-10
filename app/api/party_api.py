from typing import List
from fastapi import (Depends, APIRouter)
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from databases import Database

from ..deps import (get_db, get_current_active_user)
from ..services import party_service
from ..schemas import (
    PartyCreate, PartyUpdate, PartyGet,
    UserInDb
)

router = InferringRouter()


@cbv(router)
class PartyApi:
    db: Database = Depends(get_db)
    user: UserInDb = Depends(get_current_active_user)

    # noinspection PyTypeChecker
    @router.get("/")
    async def get_many(
            self, offset: int = 0, limit: int = 20
    ) -> List[PartyGet]:
        return await party_service.get_many(self.db, self.user, offset, limit)

    @router.get("/{uid}/")
    async def get_one(
            self, uid: str
    ) -> PartyGet:
        return await party_service.get_one_by_uid(self.db, self.user, uid)

    @router.post("/")
    async def create_one(
            self, obj: PartyCreate
    ) -> PartyGet:
        result = await party_service.create(self.db, self.user, obj)
        return {**obj.dict(), **result}

    @router.put("/{uid}/")
    async def update_one(
            self, uid: str, obj: PartyUpdate
    ) -> PartyGet:
        await party_service.update_by_uid(self.db, self.user, uid, obj)
        return {**obj.dict(), "uid": uid}

    @router.delete("/{uid}/")
    async def delete_one(
            self, uid: str
    ):
        await party_service.delete_by_uid(self.db, self.user, uid)
        return {"message": "Object with uid: {} deleted successfully!".format(uid)}
