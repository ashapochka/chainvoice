from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from ..services import party_service
from ..schemas import (
    PartyCreate, PartyUpdate, PartyGet,
)
from .base_api import BaseAPI

router = InferringRouter()


@cbv(router)
class PartyAPI(BaseAPI[PartyGet, PartyCreate, PartyUpdate]):
    service = party_service

    get_many = router.get('/')(BaseAPI.get_many)
    get_one = router.get("/{uid}/")(BaseAPI.get_one)
    create_one = router.post("/")(BaseAPI.create_one)
    update_one = router.put("/{uid}/")(BaseAPI.update_one)
    delete_one = router.delete("/{uid}/")(BaseAPI.delete_one)
