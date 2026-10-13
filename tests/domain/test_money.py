import pytest

from shop.domain.money import ZERO, Money


def test_from_pounds():
    assert Money.from_pounds("12.34") == Money(1234)
    assert Money.from_pounds(5) == Money(500)


def test_arithmetic():
    assert Money(150) + Money(250) == Money(400)
    assert Money(400) - Money(150) == Money(250)
    assert Money(150) * 3 == Money(450)
    assert -Money(150) == Money(-150)


def test_sum():
    assert Money.sum([Money(100), Money(250)]) == Money(350)
    assert Money.sum([]) == ZERO


@pytest.mark.parametrize(
    "amount, percent, expected",
    [(1000, 10, 100), (1565, 10, 157), (1, 50, 1), (999, 33, 330)],
)
def test_percent_rounds_halves_up(amount, percent, expected):
    assert Money(amount).percent(percent) == Money(expected)


def test_fraction():
    assert Money(2000).fraction(20, 120) == Money(333)


def test_str():
    assert str(Money(1234)) == "12.34"
    assert str(Money(5)) == "0.05"
    assert str(Money(-250)) == "-2.50"


def test_floor_pounds():
    assert Money(2499).floor_pounds() == 24
