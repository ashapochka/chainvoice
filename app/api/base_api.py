from fastapi import Depends
from databases import Database

from ..deps import (get_db, get_current_active_user)
from ..schemas import  UserInDb


class BaseAPI:
    db: Database = Depends(get_db)
    user: UserInDb = Depends(get_current_active_user)
