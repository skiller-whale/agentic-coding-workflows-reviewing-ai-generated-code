from shop.domain.money import Money
from shop.domain.shipping import shipping_for
from shop.domain.tax import vat_included_in

THRESHOLD = Money(5000)


def test_vat_is_included():
    assert vat_included_in(Money(6000)) == Money(1000)


def test_vat_rounds_to_the_penny():
    assert vat_included_in(Money(2000)) == Money(333)


def test_shipping_rate():
    assert shipping_for(Money(2000), THRESHOLD) == Money(495)


def test_free_shipping_at_threshold():
    assert shipping_for(Money(5000), THRESHOLD) == Money(0)
    assert shipping_for(Money(4999), THRESHOLD) == Money(495)
