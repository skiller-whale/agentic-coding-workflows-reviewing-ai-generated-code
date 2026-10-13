from shop.domain.errors import ValidationFailed
from shop.domain.models import Adjustment
from shop.domain.money import Money


def points_earned(amount_paid: Money, points_per_pound: int) -> int:
    """Points for an order, on what the customer paid for merchandise (not shipping)."""
    return amount_paid.floor_pounds() * points_per_pound


def redemption(
    points: int,
    balance: int,
    merchandise: Money,
    point_value: Money,
    max_percent: int,
) -> Adjustment:
    """The adjustment for redeeming `points` against an order."""
    if points <= 0:
        raise ValidationFailed("Redeem at least one point")
    if points > balance:
        raise ValidationFailed(f"You have {balance} points, not {points}")
    amount = point_value * points
    limit = merchandise.percent(max_percent)
    if amount > limit:
        raise ValidationFailed(
            f"Points can pay for at most {max_percent}% of the merchandise ({limit})"
        )
    return Adjustment(kind="loyalty", description=f"{points} loyalty points", amount=amount)
