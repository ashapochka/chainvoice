const test = require('ava');

const hash = require('keccak');

const {accounts, contract} = require('@openzeppelin/test-environment');

const [owner, seller, buyer] = accounts;

const TOKEN_ID = 0;
const INVOICE_DRAFT = 0;
const INVOICE_UNPAID = 1;
const INVOICE_PAID = 2;
const INVOICE_CANCELED = 3;

const INITIAL_BALANCE = 100000000000

const ChainvoiceERC1155 = contract.fromArtifact('ChainvoiceERC1155');
const InvoiceRegistry = contract.fromArtifact('InvoiceRegistry');

function keccakHash(s) {
    return '0x' + hash('keccak256').update(s).digest('hex');
}

test.before(async t => {
    t.context.tokenContract = await ChainvoiceERC1155.new(
        {from: owner}
    );
    for (let account of [seller, buyer]) {
        await t.context.tokenContract.safeTransferFrom(
            owner, account, TOKEN_ID, INITIAL_BALANCE, '0x0',
            {from: owner}
        );
    }
    t.context.invoiceRegistry = await InvoiceRegistry.new(
        t.context.tokenContract.address,
        {from: owner}
    );
});

test('invoice and pay', async t => {
    const tokenContract = t.context.tokenContract;
    const registry = t.context.invoiceRegistry;
    const invoiceId = keccakHash('invoice 1')
    const invoiceAmount = 21900 // $219.00
    await registry.registerInvoice(
        invoiceId, buyer, TOKEN_ID, invoiceAmount,
        {from: seller}
    );
    let invoice = await registry.invoices(invoiceId);
    t.is(invoice.state.toNumber(), INVOICE_DRAFT);
    await registry.publishInvoice(
        invoiceId,
        {from: seller}
    );
    invoice = await registry.invoices(invoiceId);
    t.is(invoice.state.toNumber(), INVOICE_UNPAID);
    await t.throwsAsync(async () => {
        await registry.payInvoice(
            invoiceId, owner, buyer, TOKEN_ID, invoiceAmount
        );
    });
    await tokenContract.safeTransferFrom(
        buyer, registry.address,
        TOKEN_ID, invoiceAmount,
        invoiceId,
        {from: buyer}
    );
    invoice = await registry.invoices(invoiceId);
    t.is(invoice.state.toNumber(), INVOICE_PAID);
    const buyerBalance = await tokenContract.balanceOf(buyer, TOKEN_ID);
    t.is(buyerBalance.toNumber(), INITIAL_BALANCE - invoiceAmount);
    const sellerBalance = await tokenContract.balanceOf(seller, TOKEN_ID);
    t.is(sellerBalance.toNumber(), INITIAL_BALANCE + invoiceAmount);
});
