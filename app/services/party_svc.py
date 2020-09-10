from ..db import parties
from .base_svc import BaseService


class PartyService(BaseService):
    pass


party_service = PartyService(parties)
