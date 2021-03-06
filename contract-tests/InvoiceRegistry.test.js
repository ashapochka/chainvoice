const test = require('ava');

const hash = require('keccak');

const {accounts, contract} = require('@openzeppelin/test-environment');

const [owner, seller, buyer] = accounts;

const TOKEN_ID = 0;
const INVOICE_DRAFT = 0;
const INVOICE_UNPAID = 1;
const INVOICE_PAID = 2;
const INVOICE_CANCELED = 3;

const InvoiceRegistry = contract.fromArtifact('InvoiceRegistry');

function keccakHash(s) {
    return '0x' + hash('keccak256').update(s).digest('hex');
}

test.before(async t => {
    t.context.invoiceRegistry = await InvoiceRegistry.new(
        "0x0000000000000000000000000000000000000000",
        {from: owner}
    );
});

test('the deployer is the owner', async t => {
    t.is(await t.context.invoiceRegistry.owner(), owner);
});

test('invoice and pay', async t => {
    const registry = t.context.invoiceRegistry;
    const invoiceId = keccakHash('invoice 1')
    const invoiceAmount = 21900 // $219.00
    await registry.registerInvoice(
        invoiceId, buyer, TOKEN_ID, invoiceAmount,
        {from: seller}
    );
    let invoice = await registry.invoices(invoiceId);
    t.is(invoice.state.toNumber(), INVOICE_DRAFT);
    await t.throwsAsync(async () => {
        await registry.payInvoice(
            invoiceId, owner, buyer, TOKEN_ID, invoiceAmount
        );
    });
    await registry.publishInvoice(
        invoiceId,
        {from: seller}
    );
    invoice = await registry.invoices(invoiceId);
    t.is(invoice.state.toNumber(), INVOICE_UNPAID);
    await t.throwsAsync(async () => {
        await registry.payInvoice(
            invoiceId, owner, buyer, TOKEN_ID, invoiceAmount + 100
        );
    });
    await registry.payInvoice(
        invoiceId, owner, buyer, TOKEN_ID, invoiceAmount
    );
    invoice = await registry.invoices(invoiceId);
    t.is(invoice.state.toNumber(), INVOICE_PAID);
});
