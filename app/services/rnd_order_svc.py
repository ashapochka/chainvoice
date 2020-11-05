import random
import time
from collections import Counter

from databases import Database
from fastapi import Depends

from .party_svc import PartyService
from .catalog_svc import CatalogService
from .catalog_item_svc import CatalogItemService
from .order_svc import OrderService
from .order_item_svc import OrderItemService
from ..db import get_db
from ..schemas import UserInDb, OrderCreate, OrderItemCreate


class RandomOrderService:
    def __init__(
            self,
            db: Database = Depends(get_db),
            party_service: PartyService = Depends(),
            catalog_service: CatalogService = Depends(),
            catalog_item_service: CatalogItemService = Depends(),
            order_service: OrderService = Depends(),
            order_item_service: OrderItemService = Depends(),
    ):
        self.db = db
        self.party_service = party_service
        self.catalog_service = catalog_service
        self.catalog_item_service = catalog_item_service
        self.order_service = order_service
        self.order_item_service = order_item_service

    async def create(
            self, user: UserInDb,
            max_attempts=10,
            offset=0, limit=100
    ):
        async with self.db.transaction():
            parties = await self.party_service.get_many(
                user, offset=offset, limit=limit
            )

            # select a seller
            attempts = 0
            while attempts < max_attempts:
                seller = random.choice(parties)
                catalogs = await self.catalog_service.get_many(
                    user, offset=offset, limit=limit, seller_uid=seller['uid']
                )
                if not len(catalogs) or not seller['blockchain_account_address']:
                    attempts += 1  # party cannot be a seller
                else:
                    break  # seller found
            else:
                raise Exception(
                    f'seller not found after {attempts} attempts, exiting.'
                )

            # select a buyer
            attempts = 0
            while attempts < max_attempts:
                buyer = random.choice(parties)
                if buyer is seller or not buyer['blockchain_account_address']:
                    attempts += 1  # party cannot be a buyer
                else:
                    break  # buyer found
            else:
                raise Exception(
                    f'buyer not found after {attempts} attempts, exiting.'
                )

            # buyer selects seller's catalogs to buy items from
            n_catalogs_to_select = random.randint(1, len(catalogs))
            selected_catalogs = []
            attempts = 0
            while attempts < max_attempts * n_catalogs_to_select:
                catalog = random.choice(catalogs)
                if catalog in selected_catalogs:
                    attempts += 1
                else:
                    selected_catalogs.append(catalog)
                    if len(selected_catalogs) == n_catalogs_to_select:
                        break  # buyer selected catalogs
            else:
                raise Exception(
                    f'failed to select {n_catalogs_to_select} catalogs, exiting.'
                )

            # select items to purchase from catalogs
            selected_items = []
            for catalog in selected_catalogs:
                catalog_items = await self.catalog_item_service.get_many(
                    user, offset=offset, limit=limit, catalog_uid=catalog['uid']
                )
                n_items = random.randint(1, min(5, len(catalog_items)))
                selected_items.extend(random.choices(catalog_items, k=n_items))

            # create a new order
            order = await self.order_service.create(
                user, OrderCreate(
                    seller_uid=seller['uid'],
                    customer_uid=buyer['uid'],
                    ref_id=f'PO-{int(time.time())}'
                ), tx=False
            )
            order['obj']['seller_uid'] = seller['uid']
            order['obj']['seller_name'] = seller['name']
            order['obj']['customer_uid'] = buyer['uid']
            order['obj']['customer_name'] = buyer['name']

            # create order items from selected catalog items
            order_uid = order['obj']['uid']
            item_map = {
                item['uid']: item for item in selected_items
            }
            item_quantities = dict(
                Counter(item['uid'] for item in selected_items)
            )
            for item_uid, item in item_map.items():
                await self.order_item_service.create(
                    user, OrderItemCreate(
                        order_uid=order_uid,
                        catalog_item_uid=item_uid,
                        quantity=item_quantities[item_uid],
                        base_price=item['price']
                    ), tx=False
                )

            # calculate order's total amount
            order_amount = await self.order_service.update_total_amount(
                user, order_uid, tx=False
            )
            order['obj']['amount'] = order_amount['amount']

            return order
