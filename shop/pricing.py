from dataclasses import dataclass

from shop.money import Money

SHIPPING = Money(495)
FREE_SHIPPING_FROM = Money(5000)


@dataclass(frozen=True)
class Line:
    sku: str
    price: Money
    quantity: int


@dataclass(frozen=True)
class Price:
    subtotal: Money
    shipping: Money
    total: Money


def price(lines: list[Line]) -> Price:
    subtotal = sum((line.price * line.quantity for line in lines), Money(0))
    shipping = Money(0) if subtotal >= FREE_SHIPPING_FROM else SHIPPING
    return Price(subtotal=subtotal, shipping=shipping, total=subtotal + shipping)
