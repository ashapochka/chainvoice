// SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.6.0;

import "@openzeppelin/contracts/math/SafeMath.sol";
import "@openzeppelin/contracts/token/ERC1155/ERC1155Holder.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract InvoiceRegistry is ERC1155Holder, Ownable, AccessControl {
    using SafeMath for uint256;

    enum InvoiceState {
        DRAFT, UNPAID, PAID, CANCELED
    }

    struct Invoice {
        bool isRegistered;
        bytes invoiceId;
        address seller;
        address buyer;
        uint256 tokenId;
        uint256 amount;
        uint256 paidAmount;
        InvoiceState state;
    }

    mapping(bytes => Invoice) public invoices;

    event InvoiceRegistered(
        bytes invoiceId,
        address seller,
        address buyer,
        uint256 tokenId,
        uint256 amount,
        InvoiceState state
    );

    event InvoicePublished(
        bytes invoiceId,
        address seller,
        address buyer,
        uint256 tokenId,
        uint256 amount,
        InvoiceState state
    );

    event InvoiceCanceled(
        bytes invoiceId,
        address seller,
        address buyer,
        uint256 tokenId,
        uint256 amount,
        uint256 paidAmount,
        InvoiceState state
    );

    event PaymentProcessed(
        bytes invoiceId,
        address operator,
        address from,
        address seller,
        uint256 tokenId,
        uint256 amount,
        uint256 paidAmount,
        uint256 value,
        InvoiceState state
    );

    function onERC1155Received(
        address operator,
        address from,
        uint256 id,
        uint256 value,
        bytes memory data
    ) public virtual override returns (bytes4) {
        if (processPayment(operator, from, id, value, data)) {
            return this.onERC1155Received.selector;
        } else {
            return 0;
        }
    }

    function processPayment(
        address operator,
        address from,
        uint256 tokenId,
        uint256 value,
        bytes memory invoiceId
    ) public returns (bool) {
        Invoice storage invoice = invoices[invoiceId];
        require(invoice.isRegistered, "Invoice not registered yet");
        require(
            invoice.state == InvoiceState.UNPAID,
            "Invoice does not accept payments"
        );
        uint256 paidAmount = invoice.paidAmount;
        require(
            invoice.amount >= paidAmount.add(value),
            "Payment is higher than remaining invoice amount"
        );
        invoice.paidAmount = paidAmount.add(value);
        if (invoice.amount == invoice.paidAmount) {
            invoice.state = InvoiceState.PAID;
        }
        emit PaymentProcessed(
            invoiceId, operator, from, invoice.seller, tokenId,
            invoice.amount, paidAmount, value, invoice.state
        );
        return true;
    }

    function registerInvoice(
        address buyer,
        uint256 tokenId,
        uint256 amount,
        bytes memory invoiceId) public returns (bool){
        Invoice storage invoice = invoices[invoiceId];
        require(!invoice.isRegistered, "Invoice already registered");
        invoice.isRegistered = true;
        invoice.invoiceId = invoiceId;
        invoice.seller = msg.sender;
        invoice.buyer = buyer;
        invoice.tokenId = tokenId;
        invoice.amount = amount;
        invoice.paidAmount = 0;
        invoice.state = InvoiceState.DRAFT;
        emit InvoiceRegistered(
            invoiceId, invoice.seller, buyer, tokenId, amount, invoice.state
        );
        return true;
    }

    function publishInvoice(bytes memory invoiceId) public {
        Invoice storage invoice = invoices[invoiceId];
        require(invoice.isRegistered, "Invoice not registered yet");
        require(
            msg.sender == invoice.seller,
                "Invoice publisher is different from seller"
        );
        require(
            invoice.state == InvoiceState.DRAFT,
            "Invoice is not in DRAFT mode"
        );
        invoice.state = InvoiceState.UNPAID;
        emit InvoicePublished(
            invoice.invoiceId,
            invoice.seller,
            invoice.buyer,
            invoice.tokenId,
            invoice.amount,
            invoice.state
        );
    }

    function cancelInvoice(bytes memory invoiceId) public {
        Invoice storage invoice = invoices[invoiceId];
        require(invoice.isRegistered, "Invoice not registered yet");
        require(
            msg.sender == invoice.seller,
                "Invoice canceller is different from seller"
        );
        invoice.state = InvoiceState.CANCELED;
        emit InvoiceCanceled(
            invoice.invoiceId,
            invoice.seller,
            invoice.buyer,
            invoice.tokenId,
            invoice.amount,
            invoice.paidAmount,
            invoice.state
        );
    }

    function destroy() public onlyOwner {
        selfdestruct(payable(owner()));
    }
}
