from typing import Type, Union, Dict, TypedDict
from pathlib import Path

import vyper
from web3 import Web3
from web3.contract import Contract
from web3.middleware import geth_poa_middleware
from web3.eth import Address, TxReceipt


def compile_vyper_contract(contract_file_path):
    with open(contract_file_path) as f:
        source = f.read()
        compiled_contract = vyper.compile_code(
            source, output_formats=['bytecode', 'abi'])
        return compiled_contract


# noinspection PyArgumentList
class ContractRecord:
    file_path: Path
    bytecode: bytes
    abi: list
    address: Address
    contract: Contract

    def __init__(
            self, file_path=None, bytecode=None,
            abi=None, address=None, contract=None
    ):
        self.file_path = file_path
        self.bytecode = bytecode
        self.abi = abi
        self.address = address
        self.contract = contract


class EthClient:
    endpoint_uri: str
    endpoint_ipc: str
    w3: Web3
    account_address: Address
    private_key: str
    # local, hosted, test
    node_type: str
    contract_records: Dict[Path, ContractRecord]

    def __init__(
            self,
            endpoint_uri=None,
            endpoint_ipc=None,
            account_address=None,
            keystore_path=None,
            keystore_password=None,
            geth_support=True
    ):
        if endpoint_uri:
            self.node_type = 'hosted'
            self.endpoint_uri = endpoint_uri
            self.w3 = Web3(Web3.HTTPProvider(self.endpoint_uri))
            if geth_support:
                # inject the poa compatibility middleware to the innermost layer
                self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            with open(keystore_path) as keyfile:
                encrypted_key = keyfile.read()
                self.private_key = self.w3.eth.account.decrypt(
                    encrypted_key, keystore_password)
        elif endpoint_ipc:
            self.node_type = 'local'
            self.endpoint_ipc = endpoint_ipc
            # if we want to connect to the local node
            self.w3 = Web3(Web3.IPCProvider(self.endpoint_ipc))
            if geth_support:
                # inject the poa compatibility middleware to the innermost layer
                self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        else:
            self.node_type = 'test'
            from web3 import EthereumTesterProvider
            self.w3 = Web3(EthereumTesterProvider())
        if not account_address:
            account_address = self.w3.eth.accounts[0]
        self.account_address = account_address
        self.w3.eth.defaultAccount = self.account_address
        self.contract_records = dict()

    def compile_contract(self, contract_file_path: Path) -> ContractRecord:
        compiled_contract_outputs = compile_vyper_contract(contract_file_path)
        compiled_contract = ContractRecord(
            file_path=contract_file_path,
            bytecode=compiled_contract_outputs['bytecode'],
            abi=compiled_contract_outputs['abi']
        )
        self.contract_records[contract_file_path] = compiled_contract
        return compiled_contract

    def use_existing_contract(
            self, contract_file_path: Path, contract_address: Address
    ) -> ContractRecord:
        contract_record = self.compile_contract(contract_file_path)
        contract_record.address = contract_address
        contract_record.contract = self.w3.eth.contract(
            address=contract_address, abi=contract_record.abi
        )
        return contract_record

    def deploy_contract(
            self, contract_file_path: Path, *args, **kwargs
    ) -> ContractRecord:
        contract_record = self.compile_contract(contract_file_path)
        new_contract = self.w3.eth.contract(
            abi=contract_record.abi, bytecode=contract_record.bytecode
        )
        # Submit the transaction that deploys the contract
        txn_receipt = self.send_transaction(
            None, new_contract.constructor, *args, **kwargs
        )
        contract_record.address = txn_receipt.contractAddress
        contract_record.contract = self.w3.eth.contract(
            address=contract_record.address, abi=contract_record.abi
        )
        return contract_record

    def sign_transaction(self, transaction):
        assert self.node_type == 'hosted'
        return self.w3.eth.account.signTransaction(
            transaction, self.private_key
        )

    def send_raw_transaction(self, func, *args, **kwargs) -> TxReceipt:
        assert self.node_type == 'hosted'
        transaction = func(*args, **kwargs).buildTransaction()
        estimated_gas = self.w3.eth.estimateGas(transaction)
        transaction.update({'gas': estimated_gas})
        transaction.update(
            {'nonce': self.w3.eth.getTransactionCount(self.account_address)}
        )
        signed_tx = self.sign_transaction(transaction)
        txn_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        # Wait for the transaction to be mined, and get the transaction receipt
        txn_receipt = self.w3.eth.waitForTransactionReceipt(txn_hash)
        return txn_receipt

    def send_test_transaction(
            self, caller_address, func, *args, **kwargs
    ) -> TxReceipt:
        tx_hash = func(
            *args, **kwargs
        ).transact({
            'from': caller_address if caller_address else self.account_address
        })
        return self.w3.eth.waitForTransactionReceipt(tx_hash, 180)

    def send_local_transaction(
            self, func, *args, **kwargs
    ) -> TxReceipt:
        tx_hash = func(
            *args, **kwargs
        ).transact({
            'from': self.account_address,
            # TODO: this is a quick fix for quorum failing estimateGas
            # need to fix for ethereum
            'gas': 500000
        })
        return self.w3.eth.waitForTransactionReceipt(tx_hash, 180)

    def send_transaction(
            self, caller_address, func, *args, **kwargs
    ) -> TxReceipt:
        if self.node_type == 'hosted':
            return self.send_raw_transaction(func, *args, **kwargs)
        elif self.node_type == 'local':
            # needed for local geth connection only
            # TODO: figure out correct unlock, this works for quorum
            self.w3.geth.personal.unlock_account(self.account_address, '')
            return self.send_local_transaction(func, *args, **kwargs)
        elif self.node_type == 'test':
            return self.send_test_transaction(
                caller_address, func, *args, **kwargs
            )
        else:
            raise NotImplementedError()
