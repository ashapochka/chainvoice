from eth_account.signers.local import LocalAccount
from web3.types import TxReceipt
from .base_sc import BaseContract


class InvoiceRegistryContract(BaseContract):

    def register_invoice(
            self, seller_account: LocalAccount,
            invoice_id: bytes, buyer_address:str,
            token_id: int, amount: int
    ) -> TxReceipt:
        """
        registerInvoice(
            bytes memory invoiceId,
            address buyer,
            uint256 tokenId,
            uint256 amount
        )
        :param seller_account:
        :param invoice_id:
        :param buyer_address:
        :param token_id:
        :param amount:
        :return:
        """
        contract_call = self.contract.functions.registerInvoice(
            invoice_id, buyer_address, token_id, amount
        )
        return self.send_tx(contract_call, seller_account)

    def publish_invoice(
            self, seller_account: LocalAccount, invoice_id: bytes
    ):
        """
        publishInvoice(bytes memory invoiceId)
        :param seller_account:
        :param invoice_id:
        :return:
        """
        contract_call = self.contract.functions.publishInvoice(
            invoice_id
        )
        return self.send_tx(contract_call, seller_account)

    def cancel_invoice(
            self, seller_account: LocalAccount, invoice_id: bytes
    ):
        """
        cancelInvoice(bytes memory invoiceId)
        :param seller_account:
        :param invoice_id:
        :return:
        """
        contract_call = self.contract.functions.cancelInvoice(
            invoice_id
        )
        return self.send_tx(contract_call, seller_account)

    def get_invoice(self, invoice_id: bytes):
        """
        mapping(bytes => Invoice) public invoices;
        :param invoice_id:
        :return:
        """
        return self.contract.functions.invoices(invoice_id).call()
