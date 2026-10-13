import itertools
from typing import Protocol

from shop.domain.errors import PaymentDeclined
from shop.domain.money import Money


class PaymentGateway(Protocol):
    def charge(self, amount: Money, payment_token: str) -> str:
        """Take a payment, returning the gateway's reference for it."""

    def refund(self, payment_ref: str, amount: Money) -> None: ...


class FakeGateway:
    """Stands in for the card processor. The token "tok_decline" is always declined."""

    def __init__(self):
        self._refs = (f"pay_{n:06d}" for n in itertools.count(1))
        self.charges: dict[str, Money] = {}
        self.refunds: list[tuple[str, Money]] = []

    def charge(self, amount: Money, payment_token: str) -> str:
        if payment_token == "tok_decline":
            raise PaymentDeclined("Your card was declined")
        ref = next(self._refs)
        self.charges[ref] = amount
        return ref

    def refund(self, payment_ref: str, amount: Money) -> None:
        self.refunds.append((payment_ref, amount))
