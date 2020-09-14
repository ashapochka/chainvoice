from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class OrderItemUpdate:
    """  """

    order_uid: Optional[str] = None
    catalog_item_uid: Optional[str] = None
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
    def from_dict(d: Dict[str, Any]) -> OrderItemUpdate:
        order_uid = d.get("order_uid")

        catalog_item_uid = d.get("catalog_item_uid")

        quantity = d.get("quantity")

        base_price = d.get("base_price")

        return OrderItemUpdate(
            order_uid=order_uid, catalog_item_uid=catalog_item_uid, quantity=quantity, base_price=base_price,
        )
