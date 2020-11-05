from typing import Any, Optional
from databases import Database
from fastapi import Depends

from ..db import users, get_db
from ..schemas import (UserCreate, UserUpdate, UserInDb)
from ..security import (get_password_hash, verify_password)
from ..config import get_settings
from .base_svc import BaseService


class UserService(BaseService):
    def __init__(self, db: Database = Depends(get_db)):
        super().__init__(users, db)

    async def get_one_by_username(
            self, user: UserInDb, username: str
    ) -> Optional[UserInDb]:
        user_record = await self.get_one_where(
            user, self.table.c.username == username
        )
        if not user_record:
            return None
        else:
            return UserInDb(**user_record)

    async def create(self, user: UserInDb, obj: UserCreate, tx: bool = True):
        obj_data = self._to_dict(obj)
        obj_data['hashed_password'] = get_password_hash(
            obj.password.get_secret_value()
        )
        del obj_data['password']
        return await self._insert(obj_data, tx=tx)

    async def update_where(
            self, user: UserInDb,
            where: Any, obj: UserUpdate, tx: bool = True
    ):
        obj_data = self._to_dict(obj)
        if 'password' in obj_data:
            obj_data['hashed_password'] = get_password_hash(
                obj.password.get_secret_value()
            )
            del obj_data['password']
        query = self.table.update().where(where).values(**obj_data)
        return await self._execute_in_tx(
            tx, lambda: self.db.execute(query)
        )
        # async with self.db.transaction():
        #     return await self.db.execute(query)

    async def authenticate(
            self, user: UserInDb, username: str, password: str
    ) -> Optional[UserInDb]:
        new_user = await self.get_one_by_username(user, username)
        if not new_user:
            return None
        if not verify_password(password, new_user.hashed_password):
            return None
        return new_user

    async def create_default_superuser(self, user: UserInDb):
        settings = get_settings()
        async with self.db.transaction():
            superuser = await self.get_one_by_username(
                user, settings.su_username
            )
            if not superuser:
                await self.create(user, UserCreate(
                    username=settings.su_username,
                    password=settings.su_password,
                    email=settings.su_email,
                    name=settings.su_name,
                    is_active=True,
                    is_superuser=True
                ), tx=False)
