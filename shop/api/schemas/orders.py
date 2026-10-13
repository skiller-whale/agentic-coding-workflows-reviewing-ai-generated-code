from pydantic import BaseModel, Field

from shop.api.schemas.common import money
from shop.domain.models import Adjustment, Order, OrderLine


class CheckoutIn(BaseModel):
    cart_id: int
    payment_token: str
    redeem_points: int = Field(default=0, ge=0)


class OrderLineOut(BaseModel):
    sku: str
    name: str
    unit_price: str
    quantity: int
    line_total: str

    @classmethod
    def of(cls, line: OrderLine) -> "OrderLineOut":
        return cls(
            sku=line.sku,
            name=line.name,
            unit_price=money(line.unit_price),
            quantity=line.quantity,
            line_total=money(line.line_total),
        )


class AdjustmentOut(BaseModel):
    kind: str
    description: str
    amount: str

    @classmethod
    def of(cls, adjustment: Adjustment) -> "AdjustmentOut":
        return cls(
            kind=adjustment.kind,
            description=adjustment.description,
            amount=money(adjustment.amount),
        )


class OrderOut(BaseModel):
    id: int
    status: str
    lines: list[OrderLineOut]
    adjustments: list[AdjustmentOut]
    merchandise: str
    tax: str
    shipping: str
    total: str
    loyalty_points_earned: int
    loyalty_points_redeemed: int
    placed_at: str
    dispatched_at: str | None

    @classmethod
    def of(cls, order: Order) -> "OrderOut":
        return cls(
            id=order.id,
            status=order.status.value,
            lines=[OrderLineOut.of(line) for line in order.lines],
            adjustments=[AdjustmentOut.of(adj) for adj in order.adjustments],
            merchandise=money(order.merchandise),
            tax=money(order.tax),
            shipping=money(order.shipping),
            total=money(order.total),
            loyalty_points_earned=order.loyalty_points_earned,
            loyalty_points_redeemed=order.loyalty_points_redeemed,
            placed_at=order.placed_at.isoformat(),
            dispatched_at=order.dispatched_at.isoformat() if order.dispatched_at else None,
        )
