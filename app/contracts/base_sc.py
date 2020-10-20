from web3 import Web3
from web3.contract import Contract
from eth_account.signers.local import LocalAccount
from web3.types import TxReceipt


class BaseContract:
    w3: Web3 = None
    contract: Contract = None

    def __init__(self, w3: Web3, contract_address, contract_abi):
        self.w3 = w3
        self.contract = w3.eth.contract(
            address=contract_address,
            abi=contract_abi
        )

    def send_tx(
            self, contract_call, signer: LocalAccount
    ) -> TxReceipt:
        nonce = self.w3.eth.getTransactionCount(signer.address)
        txn = contract_call.buildTransaction({
            'nonce': nonce,
            'gas': 1000000,  # TODO: make gas configurable
        })
        signed_txn = self.w3.eth.account.sign_transaction(
            txn, private_key=signer.key
        )
        txn_hash = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        txn_receipt = self.w3.eth.waitForTransactionReceipt(txn_hash)
        return txn_receipt

    def decode_tx_input(self, tx_hash: str):
        tx = self.w3.eth.getTransaction(tx_hash)
        return self.contract.decode_function_input(tx.input)
