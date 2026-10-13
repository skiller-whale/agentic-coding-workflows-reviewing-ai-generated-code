from decimal import Decimal, InvalidOperation

from shop.domain.money import Money


def money(amount: Money) -> str:
    """Amounts go over the API as strings of pounds, e.g. "12.50"."""
    return str(amount)


def parse_money(value: str) -> Money:
    try:
        pounds = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{value!r} isn't an amount of money") from exc
    if pounds != pounds.quantize(Decimal("0.01")):
        raise ValueError(f"{value!r} has fractions of a penny")
    return Money.from_pounds(pounds)


def check_money(value: str) -> str:
    """For pydantic validators: reject a string that isn't an amount of money."""
    parse_money(value)
    return value
