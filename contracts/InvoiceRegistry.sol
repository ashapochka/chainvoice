// SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.6.0;

import "@openzeppelin/contracts/math/SafeMath.sol";
import "@openzeppelin/contracts/token/ERC1155/IERC1155.sol";
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

    address constant NULL_ADDRESS = address(0x0);
    address immutable public tokenContract;
    mapping(bytes => Invoice) public invoices;

    event InvoiceStateChanged(
        bytes invoiceId,
        address seller,
        address buyer,
        uint256 tokenId,
        uint256 amount,
        uint256 paidAmount,
        InvoiceState state
    );

    event InvoicePaid(
        bytes invoiceId,
        address operator,
        address from,
        address seller,
        uint256 tokenId,
        uint256 amount,
        uint256 paidAmount,
        uint256 paymentValue,
        InvoiceState state
    );

    constructor(address _tokenContract) public {
        tokenContract = _tokenContract;
    }

    function onERC1155Received(
        address operator,
        address from,
        uint256 id,
        uint256 value,
        bytes memory data
    ) public virtual override returns (bytes4) {
        if (payInvoice(data, operator, from, id, value)) {
            return this.onERC1155Received.selector;
        } else {
            return 0;
        }
    }

//    function onERC1155Received(
//        address operator,
//        address from,
//        uint256 id,
//        uint256 value,
//        bytes memory data
//    ) public virtual override returns (bytes4) {
//        payInvoice(data, operator, from, id, value);
//        return this.onERC1155Received.selector;
//    }

    function payInvoice(
        bytes memory invoiceId,
        address operator,
        address from,
        uint256 tokenId,
        uint256 value
    ) public returns (bool) {
        require(
            tokenContract == NULL_ADDRESS || tokenContract == msg.sender,
            "Invoice must be paid via the token contract"
        );
        Invoice storage invoice = invoices[invoiceId];
        require(invoice.isRegistered, "Invoice not registered yet");
        require(
            tokenId == invoice.tokenId,
            "Payment token id is different from invoice token id"
        );
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
        if (tokenContract != NULL_ADDRESS) {
            IERC1155 erc1155 = IERC1155(tokenContract);
            erc1155.safeTransferFrom(
                address(this), invoice.seller,
                invoice.tokenId, value, abi.encode(invoice.invoiceId)
            );
        }
        emit InvoicePaid(
            invoiceId, operator, from, invoice.seller, invoice.tokenId,
            invoice.amount, invoice.paidAmount, value, invoice.state
        );
        return true;
    }

    function registerInvoice(
        bytes memory invoiceId,
        address buyer,
        uint256 tokenId,
        uint256 amount
    ) public {
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
        emit InvoiceStateChanged(
            invoice.invoiceId,
            invoice.seller,
            invoice.buyer,
            invoice.tokenId,
            invoice.amount,
            invoice.paidAmount,
            invoice.state
        );
    }

    function registerInvoice1(
        bytes memory invoiceId,
        address buyer,
        uint256 tokenId,
        uint256 amount
    ) public {
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
        emit InvoiceStateChanged(
            invoice.invoiceId,
            invoice.seller,
            invoice.buyer,
            invoice.tokenId,
            invoice.amount,
            invoice.paidAmount,
            invoice.state
        );
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
        emit InvoiceStateChanged(
            invoice.invoiceId,
            invoice.seller,
            invoice.buyer,
            invoice.tokenId,
            invoice.amount,
            invoice.paidAmount,
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
        emit InvoiceStateChanged(
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
