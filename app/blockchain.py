from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
import json
from databases import Database

from app.config import get_settings
from app.contracts import ERC1155Contract
from app.services import (blockchain_contract_service, party_service)
from app.schemas import (
    BlockchainContractGet, BlockchainContractCreate,
    PartyGet
)


class BlockchainClient:
    w3: Web3
    erc1155_contract: ERC1155Contract

    def __init__(self):
        s = get_settings()
        qnode_url = s.qnode_url
        qnode_key = s.qnode_key
        self.w3 = Web3(Web3.HTTPProvider(f'{qnode_url}/{qnode_key}'))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    async def init_contracts(self, db: Database):
        contract_record = await blockchain_contract_service.get_one_by_name(
            db, None, "ChainvoiceERC1155"
        )
        if contract_record is None:
            s = get_settings()
            contract_path = s.compiled_contracts_path / 'ChainvoiceERC1155.json'
            with open(contract_path) as f:
                compiled_contract = json.load(f)
                contract_abi = compiled_contract['abi']
            contract_address = s.erc1155_contract_address
            qadmin = await party_service.get_one_by_name(
                db, None, 'qadmin'
            )
            qadmin_party = PartyGet(**qadmin)
            new_record = BlockchainContractCreate(
                owner_uid=qadmin_party.uid,
                name='ChainvoiceERC1155',
                contract_address=contract_address,
                contract_abi=json.dumps(contract_abi)
            )
            await blockchain_contract_service.create(db, None, new_record)
        else:
            contract = BlockchainContractGet(**contract_record)
            contract_abi = contract.contract_abi
            contract_address = contract.contract_address
        self.erc1155_contract = ERC1155Contract(
            self.w3, contract_abi, contract_address
        )


blockchain_client = BlockchainClient()
