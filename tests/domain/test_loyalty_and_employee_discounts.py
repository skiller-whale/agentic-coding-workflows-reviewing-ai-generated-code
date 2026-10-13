import pytest

from shop.domain import loyalty
from shop.domain.employee_discounts import check_percent, employee_discount
from shop.domain.errors import ValidationFailed
from shop.domain.money import Money


def test_points_per_whole_pound():
    assert loyalty.points_earned(Money(2495), 1) == 24
    assert loyalty.points_earned(Money(2495), 2) == 48


def test_redemption():
    adjustment = loyalty.redemption(500, 800, Money(2000), Money(1), 50)
    assert adjustment.kind == "loyalty"
    assert adjustment.amount == Money(500)


def test_redemption_needs_enough_points():
    with pytest.raises(ValidationFailed, match="800 points"):
        loyalty.redemption(900, 800, Money(5000), Money(1), 50)


def test_redemption_capped_at_half_the_merchandise():
    with pytest.raises(ValidationFailed, match="50%"):
        loyalty.redemption(1001, 5000, Money(2000), Money(1), 50)


def test_redeem_at_least_one_point():
    with pytest.raises(ValidationFailed):
        loyalty.redemption(0, 100, Money(2000), Money(1), 50)


def test_employee_discount():
    adjustment = employee_discount(Money(1565), 10)
    assert adjustment.kind == "employee"
    assert adjustment.amount == Money(157)


def test_no_employee_discount():
    assert employee_discount(Money(2000), 0) is None


def test_employee_discount_limits():
    check_percent(0)
    check_percent(50)
    with pytest.raises(ValidationFailed):
        check_percent(51)
    with pytest.raises(ValidationFailed):
        check_percent(-1)
