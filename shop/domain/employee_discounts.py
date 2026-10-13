from shop.domain.errors import ValidationFailed
from shop.domain.models import Adjustment
from shop.domain.money import Money

MAX_PERCENT = 50


def check_percent(percent: int) -> None:
    if not 0 <= percent <= MAX_PERCENT:
        raise ValidationFailed(f"Employee discounts must be between 0 and {MAX_PERCENT}%")


def employee_discount(merchandise: Money, percent: int) -> Adjustment | None:
    """The adjustment for a staff member's discount, or None if they don't get one."""
    amount = merchandise.percent(percent)
    if amount.is_zero():
        return None
    return Adjustment(kind="employee", description=f"{percent}% employee discount", amount=amount)
