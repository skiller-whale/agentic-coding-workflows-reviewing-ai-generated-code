from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Money:
    """An amount in pounds sterling, held as a whole number of pence."""

    pence: int

    @classmethod
    def parse(cls, pounds: str) -> Money:
        """Parse an amount like "12.50"."""
        whole, pence = pounds.split(".")
        return cls(int(whole) * 100 + int(pence))

    def __add__(self, other: Money) -> Money:
        return Money(self.pence + other.pence)

    def __sub__(self, other: Money) -> Money:
        return Money(self.pence - other.pence)

    def __mul__(self, quantity: int) -> Money:
        return Money(self.pence * quantity)

    def __str__(self) -> str:
        return f"{self.pence // 100}.{self.pence % 100:02d}"
