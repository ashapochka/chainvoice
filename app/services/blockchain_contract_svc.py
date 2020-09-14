from ..db import blockchain_contracts
from .base_svc import BaseService


class BlockchainContractService(BaseService):
    pass


blockchain_contract_service = BlockchainContractService(blockchain_contracts)
