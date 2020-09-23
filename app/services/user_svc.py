from typing import Any, Optional
from databases import Database
from fastapi.encoders import jsonable_encoder

from ..db import users
from ..schemas import (UserCreate, UserUpdate, UserInDb)
from ..security import (get_password_hash, verify_password)
from ..config import get_settings
from .base_svc import BaseService
from .utils import new_uid


class UserService(BaseService):
    async def get_one_by_username(
            self, db: Database, user: UserInDb, username: str
    ) -> Optional[UserInDb]:
        return UserInDb(
            **await self.get_one_where(
                db, user, self.table.c.username == username
            )
        )

    async def create(self, db: Database, user: UserInDb, obj: UserCreate):
        obj_data = self._to_dict(obj)
        obj_data['hashed_password'] = get_password_hash(obj.password)
        del obj_data['password']
        return await self._insert(db, obj_data)

    async def update_where(
            self, db: Database, user: UserInDb,
            where: Any, obj: UserUpdate
    ):
        obj_data = self._to_dict(obj)
        if 'password' in obj_data:
            obj_data['hashed_password'] = get_password_hash(obj.password)
            del obj_data['password']
        query = self.table.update().where(where).values(**obj_data)
        async with db.transaction():
            return await db.execute(query)

    async def authenticate(
            self, db: Database, user: UserInDb, username: str, password: str
    ) -> Optional[UserInDb]:
        new_user = await self.get_one_by_username(db, user, username)
        if not new_user:
            return None
        if not verify_password(password, new_user.hashed_password):
            return None
        return new_user

    async def create_default_superuser(self, db: Database, user: UserInDb):
        settings = get_settings()
        async with db.transaction():
            superuser = await self.get_one_by_username(
                db, user, settings.su_username
            )
            if not superuser:
                await self.create(db, user, UserCreate(
                    username=settings.su_username,
                    password=settings.su_password,
                    email=settings.su_email,
                    name=settings.su_name,
                    is_active=True,
                    is_superuser=True
                ))


user_service = UserService(users)
