import pytest

from shop.domain.errors import Conflict, NotFound, ValidationFailed
from shop.domain.money import Money


def test_register(services):
    customer, token = services.customers.register("Alice@Example.com ", "Alice")
    assert customer.email == "alice@example.com"
    assert services.tokens.resolve(token) == ("customer", customer.id)


def test_register_twice(services):
    services.customers.register("alice@example.com", "Alice")
    with pytest.raises(Conflict):
        services.customers.register("alice@example.com", "Alice")


def test_register_bad_email(services):
    with pytest.raises(ValidationFailed):
        services.customers.register("alice", "Alice")


def test_set_employee_discount_is_audited(services, make):
    staff, _ = make.staff()
    customer, _ = make.customer()
    updated = services.customers.set_employee_discount(staff, customer.id, 20)
    assert updated.employee_discount_percent == 20
    [entry] = services.audit.entries(subject=f"customer:{customer.id}")
    assert (entry.action, entry.details) == (
        "customer.employee_discount_changed",
        {"old": 0, "new": 20},
    )


def test_employee_discount_is_capped(services, make):
    staff, _ = make.staff()
    customer, _ = make.customer()
    with pytest.raises(ValidationFailed, match="50%"):
        services.customers.set_employee_discount(staff, customer.id, 60)


def test_cart_quantities(services, make):
    make.product("TEE")
    customer, _ = make.customer()
    cart = services.carts.create(customer)
    services.carts.set_quantity(customer, cart.id, "TEE", 2)
    services.carts.set_quantity(customer, cart.id, "TEE", 3)
    assert [(line.sku, line.quantity) for line in services.carts.get(customer, cart.id).lines] == [
        ("TEE", 3)
    ]
    services.carts.set_quantity(customer, cart.id, "TEE", 0)
    assert services.carts.get(customer, cart.id).lines == []


def test_cart_quantity_limits(services, make):
    make.product("TEE")
    customer, _ = make.customer()
    cart = services.carts.create(customer)
    with pytest.raises(ValidationFailed):
        services.carts.set_quantity(customer, cart.id, "TEE", 21)


def test_cart_unknown_product(services, make):
    customer, _ = make.customer()
    cart = services.carts.create(customer)
    with pytest.raises(NotFound):
        services.carts.set_quantity(customer, cart.id, "NOPE", 1)


def test_cart_preview(services, make):
    make.product("TEE", price="20.00")
    customer, _ = make.customer()
    cart_id = make.cart(customer, ("TEE", 1))
    assert services.carts.preview(customer, cart_id).total == Money(2495)
