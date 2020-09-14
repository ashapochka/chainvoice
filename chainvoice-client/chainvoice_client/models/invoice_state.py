from enum import Enum


class InvoiceState(str, Enum):
    DRAFT = "DRAFT"
    UNPAID = "UNPAID"
    PAID = "PAID"
    CANCELED = "CANCELED"
