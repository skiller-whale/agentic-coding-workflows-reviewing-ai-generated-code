from shop.money import Money
from shop.pricing import Line, price


def test_subtotal_is_the_sum_of_the_lines():
    lines = [Line("MUG", Money(800), 2), Line("TEE", Money(1500), 1)]
    assert price(lines).subtotal == Money(3100)


def test_shipping_is_charged_under_50_pounds():
    result = price([Line("TEE", Money(4999), 1)])
    assert result.shipping == Money(495)
    assert result.total == Money(5494)


def test_shipping_is_free_from_50_pounds():
    result = price([Line("TEE", Money(5000), 1)])
    assert result.shipping == Money(0)
    assert result.total == Money(5000)
