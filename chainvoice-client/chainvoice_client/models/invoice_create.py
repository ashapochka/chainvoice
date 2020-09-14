from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Any, Dict, Optional, cast

from .invoice_state import InvoiceState


@dataclass
class InvoiceCreate:
    """  """

    order_uid: str
    ref_id: Optional[str] = None
    due_date: Optional[datetime.date] = None
    state: Optional[InvoiceState] = None

    def to_dict(self) -> Dict[str, Any]:
        order_uid = self.order_uid
        ref_id = self.ref_id
        due_date = self.due_date.isoformat() if self.due_date else None

        state = self.state.value if self.state else None

        return {
            "order_uid": order_uid,
            "ref_id": ref_id,
            "due_date": due_date,
            "state": state,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> InvoiceCreate:
        order_uid = d["order_uid"]

        ref_id = d.get("ref_id")

        due_date = None
        if d.get("due_date") is not None:
            due_date = datetime.date.fromisoformat(cast(str, d.get("due_date")))

        state = None
        if d.get("state") is not None:
            state = InvoiceState(d.get("state"))

        return InvoiceCreate(order_uid=order_uid, ref_id=ref_id, due_date=due_date, state=state,)
