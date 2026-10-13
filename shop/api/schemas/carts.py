from pydantic import BaseModel, Field

from shop.api.schemas.common import money
from shop.domain.models import Cart
from shop.domain.pricing import PriceBreakdown


class CartLineIn(BaseModel):
    quantity: int = Field(ge=0)


class CartLineOut(BaseModel):
    sku: str
    quantity: int


class PreviewOut(BaseModel):
    merchandise: str
    tax: str
    shipping: str
    total: str

    @classmethod
    def of(cls, breakdown: PriceBreakdown) -> "PreviewOut":
        return cls(
            merchandise=money(breakdown.merchandise),
            tax=money(breakdown.tax),
            shipping=money(breakdown.shipping),
            total=money(breakdown.total),
        )


class CartOut(BaseModel):
    id: int
    lines: list[CartLineOut]
    preview: PreviewOut

    @classmethod
    def of(cls, cart: Cart, breakdown: PriceBreakdown) -> "CartOut":
        return cls(
            id=cart.id,
            lines=[CartLineOut(sku=line.sku, quantity=line.quantity) for line in cart.lines],
            preview=PreviewOut.of(breakdown),
        )
