from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
import json
from databases import Database

from app.config import get_settings
from app.contracts import ERC1155Contract
from app.services import blockchain_contract_service
from app.schemas import BlockchainContractGet


class BlockchainClient:
    w3: Web3
    erc1155_contract: ERC1155Contract

    def __init__(self):
        qnode_url = get_settings().qnode_url
        qnode_key = get_settings().qnode_key
        self.w3 = Web3(Web3.HTTPProvider(f'{qnode_url}/{qnode_key}'))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    async def init_contracts(self, db: Database):
        contract_record: BlockchainContractGet = \
            await blockchain_contract_service.get_one_by_name(
                db, None, "ChainvoiceERC1155"
            )

        self.erc1155_contract = ERC1155Contract(
            self.w3,
            contract_record.contract_abi,
            contract_record.contract_address
        )


blockchain_client = BlockchainClient()
