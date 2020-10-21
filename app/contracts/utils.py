from uuid import UUID

from web3 import Web3
from web3.types import TxReceipt


class Error(Exception):
    pass


class BlockchainTransactionError(Exception):
    tx_receipt: TxReceipt

    def __init__(self, tx_receipt: TxReceipt = None):
        self.tx_receipt = tx_receipt
        super().__init__(
            f"Transaction {tx_receipt['transactionHash']} failed "
            f"with status {tx_receipt['status']}"
        )


def check_tx_success(tx_receipt: TxReceipt, raise_on_failure=False) -> bool:
    if tx_receipt['status'] == 1:
        return True
    elif raise_on_failure:
        raise BlockchainTransactionError(tx_receipt=tx_receipt)
    else:
        return False


def uuid_to_hex(uid: UUID):
    return Web3.toHex(uid.int)
