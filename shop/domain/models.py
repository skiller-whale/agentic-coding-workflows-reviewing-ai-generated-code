from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from shop.domain.money import Money


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    description: str
    category: str
    # The price shown to the customer, including VAT.
    price: Money


@dataclass(frozen=True)
class Customer:
    id: int
    email: str
    name: str
    loyalty_balance: int
    created_at: datetime
    employee_discount_percent: int = 0


@dataclass(frozen=True)
class StaffMember:
    id: int
    email: str
    name: str


@dataclass(frozen=True)
class CartLine:
    sku: str
    quantity: int


@dataclass(frozen=True)
class Cart:
    id: int
    customer_id: int
    lines: list[CartLine] = field(default_factory=list)


@dataclass(frozen=True)
class OrderLine:
    sku: str
    name: str
    unit_price: Money
    quantity: int

    @property
    def line_total(self) -> Money:
        return self.unit_price * self.quantity


@dataclass(frozen=True)
class Adjustment:
    """A reduction in the price of an order, e.g. an employee discount or loyalty points.

    `amount` is positive, and comes off the merchandise before tax is worked out.
    """

    kind: str
    description: str
    amount: Money


class OrderStatus(StrEnum):
    PLACED = "placed"
    DISPATCHED = "dispatched"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Order:
    id: int
    customer_id: int
    status: OrderStatus
    lines: list[OrderLine]
    adjustments: list[Adjustment]
    merchandise: Money
    tax: Money
    shipping: Money
    total: Money
    loyalty_points_earned: int
    loyalty_points_redeemed: int
    payment_ref: str
    placed_at: datetime
    dispatched_at: datetime | None = None


@dataclass(frozen=True)
class AuditEntry:
    id: int
    staff_id: int
    action: str
    subject: str
    details: dict
    created_at: datetime
