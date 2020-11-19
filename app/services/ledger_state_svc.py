from operator import itemgetter, attrgetter

from fastapi import Depends
from web3 import Web3

from ..blockchain import get_erc1155_contract, get_invoice_registry_contract
from ..contracts import ERC1155Contract, InvoiceRegistryContract
from ..schemas import (UserInDb, TransactionGet, List)


class LedgerStateService:
    def __init__(
            self,
            token_contract: ERC1155Contract = Depends(
                get_erc1155_contract
            ),
            invoice_registry: InvoiceRegistryContract = Depends(
                get_invoice_registry_contract
            )
    ):
        self.token_contract = token_contract
        self.invoice_registry = invoice_registry

    # noinspection DuplicatedCode,PyUnusedLocal
    async def get_many(
            self, user: UserInDb, offset, limit, **kwargs
    ) -> List[TransactionGet]:
        w3 = self.invoice_registry.w3
        last_block_number = w3.eth.block_number()
        paid_event_type = self.invoice_registry.contract.events.InvoicePaid
        paid_events = paid_event_type.createFilter(
            fromBlock=0, toBlock=last_block_number
        ).get_all_entries()
        transfer_event_type = self.token_contract.contract.events.TransferSingle
        transfer_events = transfer_event_type.createFilter(
            fromBlock=0, toBlock=last_block_number
        ).get_all_entries()
        entries = []
        for event in paid_events:
            tx_hash = event.transactionHash
            tx = w3.eth.getTransaction(tx_hash)
            tx_input = self.token_contract.contract.decode_function_input(
                tx.input
            )
            tx_args = tx_input[1]
            tx_args['data'] = Web3.toHex(tx_input[1]['data'])
            paid_event_entry = {
                'name': event.event,
                'args': dict(event.args),
                'address': event.address,
                'log_index': event.logIndex
            }
            paid_event_entry['args']['invoiceId'] = Web3.toHex(
                event.args.invoiceId)
            transfer_event_entries = [
                {
                    'name': event.event,
                    'args': dict(event.args),
                    'address': event.address,
                    'log_index': event.logIndex
                } for event in transfer_events if
                event.transactionHash == tx_hash
            ]
            tx_entry = TransactionGet(
                hash=Web3.toHex(tx_hash),
                block_number=tx.blockNumber,
                index_in_block=tx.transactionIndex,
                from_address=tx['from'],
                to_address=tx['to'],
                input={
                    'contract': 'ChainvoiceERC1155',
                    'address': tx_input[0].address,
                    'function': str(tx_input[0]),
                    'args': tx_args
                },
                events=sorted([
                    paid_event_entry,
                    *transfer_event_entries
                ], key=itemgetter('log_index'))
            )
            entries.append(tx_entry)
        entries.sort(
            key=attrgetter('block_number', 'index_in_block'), reverse=True
        )
        return entries
