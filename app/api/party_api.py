from typing import List
from fastapi import (Depends, APIRouter)
from ..deps import (get_db, get_current_active_user)
from ..services.party_svc import party_service
from ..schemas.party import (PartyCreate, PartyUpdate, PartyGet)

router = APIRouter()


# noinspection PyTypeChecker
@router.get("/", response_model=List[PartyGet])
async def get_many(
        db=Depends(get_db),
        user=Depends(get_current_active_user),
        offset: int = 0, limit: int = 20):
    return await party_service.get_many(db, offset, limit)


@router.get("/{uid}/", response_model=PartyGet)
async def get_one(*, db=Depends(get_db), uid: str):
    return await party_service.get_one_by_uid(db, uid)


@router.post("/", response_model=PartyGet)
async def create_one(*, db=Depends(get_db), obj: PartyCreate):
    result = await party_service.create(db, obj)
    return {**obj.dict(), **result}


@router.put("/{uid}/", response_model=PartyGet)
async def update_one(*, db=Depends(get_db), uid: str, obj: PartyUpdate):
    await party_service.update_by_uid(db, uid, obj)
    return {**obj.dict(), "uid": uid}


@router.delete("/{uid}/")
async def delete_one(*, db=Depends(get_db), uid: str):
    await party_service.delete_by_uid(db, uid)
    return {"message": "Object with uid: {} deleted successfully!".format(uid)}
