from eth_account.signers.local import LocalAccount
from web3.types import TxReceipt
from .base_sc import BaseContract


class ERC1155Contract(BaseContract):
    def safe_transfer_from(
            self, signer: LocalAccount,
            from_address: str, to_address: str,
            token_id: int, amount: int,
            data: str
    ) -> TxReceipt:
        contract_call = self.contract.functions.safeTransferFrom(
            from_address, to_address, token_id, amount, data
        )
        return self.send_tx(contract_call, signer)

    def balance_of(self, account: str, token_id: int) -> int:
        return self.contract.functions.balanceOf(account, token_id).call()
