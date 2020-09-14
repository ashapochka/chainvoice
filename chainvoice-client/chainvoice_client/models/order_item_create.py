from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class OrderItemCreate:
    """  """

    order_uid: str
    catalog_item_uid: str
    quantity: Optional[int] = 1
    base_price: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        order_uid = self.order_uid
        catalog_item_uid = self.catalog_item_uid
        quantity = self.quantity
        base_price = self.base_price

        return {
            "order_uid": order_uid,
            "catalog_item_uid": catalog_item_uid,
            "quantity": quantity,
            "base_price": base_price,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> OrderItemCreate:
        order_uid = d["order_uid"]

        catalog_item_uid = d["catalog_item_uid"]

        quantity = d.get("quantity")

        base_price = d.get("base_price")

        return OrderItemCreate(
            order_uid=order_uid, catalog_item_uid=catalog_item_uid, quantity=quantity, base_price=base_price,
        )
