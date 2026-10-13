import pytest

from shop.domain.errors import Conflict, ValidationFailed
from shop.domain.money import Money


def test_create_product_is_audited(services, make):
    staff, _ = make.staff()
    product = services.catalog.create_product(staff, "SCARF", "Scarf", "clothing", Money(2500))
    assert services.catalog.get_product("SCARF") == product
    [entry] = services.audit.entries(subject="product:SCARF")
    assert (entry.action, entry.details) == ("product.created", {"price": "25.00"})


def test_duplicate_sku(services, make):
    staff, _ = make.staff()
    make.product("SCARF")
    with pytest.raises(Conflict):
        services.catalog.create_product(staff, "SCARF", "Scarf", "clothing", Money(2500))


def test_price_must_be_positive(services, make):
    staff, _ = make.staff()
    with pytest.raises(ValidationFailed):
        services.catalog.create_product(staff, "SCARF", "Scarf", "clothing", Money(0))


def test_change_price_is_audited(services, make):
    staff, _ = make.staff()
    make.product("TEE", price="20.00")
    services.catalog.change_price(staff, "TEE", Money(2200))
    assert services.catalog.get_product("TEE").price == Money(2200)
    [entry] = services.audit.entries(subject="product:TEE")
    assert entry.details == {"old": "20.00", "new": "22.00"}
