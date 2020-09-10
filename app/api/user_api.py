from typing import List
from fastapi import (Depends, APIRouter)
from ..deps import (get_db, get_current_active_user)
from ..services import user_service
from ..schemas import (
    UserCreate, UserUpdate, UserGet,
    UserInDb
)

router = APIRouter()


# noinspection PyTypeChecker
@router.get("/", response_model=List[UserGet])
async def get_many(
        db=Depends(get_db),
        user: UserInDb = Depends(get_current_active_user),
        offset: int = 0, limit: int = 20
):
    return await user_service.get_many(db, user, offset, limit)


@router.get("/{uid}/", response_model=UserGet)
async def get_one(
        *, db=Depends(get_db),
        user: UserInDb = Depends(get_current_active_user),
        uid: str
):
    return await user_service.get_one_by_uid(db, user, uid)


@router.post("/", response_model=UserGet)
async def create_one(
        *, db=Depends(get_db),
        user: UserInDb = Depends(get_current_active_user),
        obj: UserCreate
):
    result = await user_service.create(db, user, obj)
    return {**obj.dict(), **result}


@router.put("/{uid}/", response_model=UserGet)
async def update_one(
        *, db=Depends(get_db),
        user: UserInDb = Depends(get_current_active_user),
        uid: str, obj: UserUpdate
):
    await user_service.update_by_uid(db, user, uid, obj)
    return {**obj.dict(), "uid": uid}


@router.delete("/{uid}/")
async def delete_one(
        *, db=Depends(get_db),
        user: UserInDb = Depends(get_current_active_user),
        uid: str
):
    await user_service.delete_by_uid(db, user, uid)
    return {"message": "Object with uid: {} deleted successfully!".format(uid)}
