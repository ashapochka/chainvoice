from eth_account.signers.local import LocalAccount
from web3.types import TxReceipt
from .base_sc import BaseContract


class InvoiceRegistryContract(BaseContract):

    def register_invoice(
            self, seller_account: LocalAccount,
            invoice_id: str, buyer_address: str,
            token_id: int, amount: int
    ) -> TxReceipt:
        """
        registerInvoice(
            uint256 invoiceId,
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
            self, seller_account: LocalAccount, invoice_id: str
    ) -> TxReceipt:
        """
        publishInvoice(uint256 invoiceId)
        :param seller_account:
        :param invoice_id:
        :return:
        """
        contract_call = self.contract.functions.publishInvoice(
            invoice_id
        )
        return self.send_tx(contract_call, seller_account)

    def cancel_invoice(
            self, seller_account: LocalAccount, invoice_id: str
    ) -> TxReceipt:
        """
        cancelInvoice(uint256 invoiceId)
        :param seller_account:
        :param invoice_id:
        :return:
        """
        contract_call = self.contract.functions.cancelInvoice(
            invoice_id
        )
        return self.send_tx(contract_call, seller_account)

    def get_invoice(self, invoice_id: str):
        """
        mapping(uint256 => Invoice) public invoices;
        :param invoice_id:
        :return:
        """
        return self.contract.functions.invoices(invoice_id).call()
