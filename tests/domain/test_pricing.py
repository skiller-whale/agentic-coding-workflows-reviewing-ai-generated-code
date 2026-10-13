import pytest

from shop.domain.errors import ValidationFailed
from shop.domain.models import Adjustment, OrderLine
from shop.domain.money import Money
from shop.domain.pricing import price

THRESHOLD = Money(5000)
TEE = OrderLine("TEE", "Tee", Money(2000), 1)
HOODIE = OrderLine("HOODIE", "Hoodie", Money(5500), 1)


def reduction(pence: int) -> Adjustment:
    return Adjustment(kind="test", description="test", amount=Money(pence))


def test_total_includes_vat():
    breakdown = price([TEE], [], THRESHOLD)
    assert breakdown.merchandise == Money(2000)
    assert breakdown.tax == Money(333)
    assert breakdown.shipping == Money(495)
    assert breakdown.total == Money(2495)


def test_quantities_and_lines():
    lines = [OrderLine("TEE", "Tee", Money(2000), 2), HOODIE]
    breakdown = price(lines, [], THRESHOLD)
    assert breakdown.merchandise == Money(9500)
    assert breakdown.tax == Money(1583)
    assert breakdown.total == Money(9500)


def test_adjustments_come_off_before_tax():
    breakdown = price([TEE], [reduction(200)], THRESHOLD)
    assert breakdown.taxable == Money(1800)
    assert breakdown.tax == Money(300)
    assert breakdown.total == Money(1800 + 495)


def test_adjustments_dont_lose_free_shipping():
    breakdown = price([HOODIE], [reduction(1100)], THRESHOLD)
    assert breakdown.shipping == Money(0)
    assert breakdown.total == Money(4400)


def test_adjustments_cant_exceed_merchandise():
    with pytest.raises(ValidationFailed):
        price([TEE], [reduction(2001)], THRESHOLD)
