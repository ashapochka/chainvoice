from eth_account.signers.local import LocalAccount
from web3.types import TxReceipt


class ERC1155Contract:
    w3 = None
    contract = None

    def __init__(self, w3, contract_abi, contract_address):
        self.w3 = w3
        self.contract = w3.eth.contract(
            address=contract_address,
            abi=contract_abi
        )

    def safe_transfer_from(
            self, signer: LocalAccount,
            from_address: str, to_address:str,
            token_id: int, amount: int,
            data: bytes
    ) -> TxReceipt:
        contract_call = self.contract.functions.safeTransferFrom(
            from_address, to_address, token_id, amount, data
        )
        return self.send_tx(contract_call, signer)

    def balance_of(self, account: str, token_id: int) -> int:
        return self.contract.functions.balanceOf(account, token_id).call()

    def send_tx(self, contract_call, signer):
        nonce = self.w3.eth.getTransactionCount(signer.address)
        txn = contract_call.buildTransaction({
            'nonce': nonce,
            'gas': 100000
        })
        signed_txn = self.w3.eth.account.sign_transaction(
            txn, private_key=signer.key
        )
        txn_hash = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        txn_receipt = self.w3.eth.waitForTransactionReceipt(txn_hash)
        return txn_receipt
