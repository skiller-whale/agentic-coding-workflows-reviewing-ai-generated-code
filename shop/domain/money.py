from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal


@dataclass(frozen=True, order=True)
class Money:
    """An amount of pounds sterling, held as a whole number of pence."""

    pence: int

    @classmethod
    def from_pounds(cls, pounds: str | int | Decimal) -> Money:
        amount = Decimal(pounds) * 100
        return cls(int(amount.quantize(Decimal(1), rounding=ROUND_HALF_UP)))

    @classmethod
    def sum(cls, amounts: Iterable[Money]) -> Money:
        return cls(sum(amount.pence for amount in amounts))

    def __add__(self, other: Money) -> Money:
        return Money(self.pence + other.pence)

    def __sub__(self, other: Money) -> Money:
        return Money(self.pence - other.pence)

    def __mul__(self, quantity: int) -> Money:
        return Money(self.pence * quantity)

    def __neg__(self) -> Money:
        return Money(-self.pence)

    def percent(self, percent: int | Decimal) -> Money:
        """`percent` per cent of this amount, rounded to the nearest penny (halves up)."""
        return self.fraction(Decimal(percent), 100)

    def fraction(self, numerator: int | Decimal, denominator: int | Decimal) -> Money:
        """This amount times numerator / denominator, rounded to the nearest penny (halves up)."""
        exact = Decimal(self.pence) * Decimal(numerator) / Decimal(denominator)
        return Money(int(exact.quantize(Decimal(1), rounding=ROUND_HALF_UP)))

    def floor_pounds(self) -> int:
        return self.pence // 100

    def is_zero(self) -> bool:
        return self.pence == 0

    def __str__(self) -> str:
        sign = "-" if self.pence < 0 else ""
        return f"{sign}{abs(self.pence) // 100}.{abs(self.pence) % 100:02d}"


ZERO = Money(0)
