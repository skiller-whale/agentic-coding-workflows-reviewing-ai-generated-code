import pytest

from shop.domain.errors import NotFound, PaymentDeclined, ValidationFailed
from shop.domain.money import Money


def test_places_order(services, make, gateway, frozen_clock):
    make.product("TEE", price="20.00")
    customer, _ = make.customer()
    cart_id = make.cart(customer, ("TEE", 2))

    order = services.checkout.place_order(customer, cart_id, "tok_visa")

    assert order.total == Money(4495)
    assert order.placed_at == frozen_clock
    assert gateway.charges[order.payment_ref] == Money(4495)


def test_clears_the_cart(services, make):
    make.product("TEE")
    customer, _ = make.customer()
    cart_id = make.cart(customer, ("TEE", 1))
    services.checkout.place_order(customer, cart_id, "tok_visa")
    with pytest.raises(NotFound):
        services.carts.get(customer, cart_id)


def test_earns_loyalty_on_merchandise_paid(services, make):
    make.product("TEE", price="20.00")
    customer, _ = make.customer()
    order = services.checkout.place_order(customer, make.cart(customer, ("TEE", 1)), "tok_visa")
    assert order.loyalty_points_earned == 20
    assert services.customers.get(customer.id).loyalty_balance == 20


def test_redeems_loyalty_points(services, make):
    make.product("HOODIE", price="55.00")
    customer, _ = make.customer(loyalty=1000)
    cart_id = make.cart(customer, ("HOODIE", 1))

    order = services.checkout.place_order(customer, cart_id, "tok_visa", redeem_points=1000)

    assert [(a.kind, a.amount) for a in order.adjustments] == [("loyalty", Money(1000))]
    assert order.total == Money(4500)
    assert order.shipping == Money(0)
    assert order.loyalty_points_redeemed == 1000
    assert order.loyalty_points_earned == 45
    assert services.customers.get(customer.id).loyalty_balance == 45


def test_employee_discount(services, make):
    make.product("TEE", price="20.00")
    customer, _ = make.customer(employee_discount=20)
    order = services.checkout.place_order(customer, make.cart(customer, ("TEE", 1)), "tok_visa")
    assert [(a.kind, a.amount) for a in order.adjustments] == [("employee", Money(400))]
    assert order.tax == Money(267)
    assert order.total == Money(1600 + 495)
    assert order.loyalty_points_earned == 16


def test_employee_discount_and_loyalty_points(services, make):
    make.product("HOODIE", price="55.00")
    customer, _ = make.customer(loyalty=1000, employee_discount=20)
    cart_id = make.cart(customer, ("HOODIE", 1))

    order = services.checkout.place_order(customer, cart_id, "tok_visa", redeem_points=1000)

    assert [(a.kind, a.amount) for a in order.adjustments] == [
        ("employee", Money(1100)),
        ("loyalty", Money(1000)),
    ]
    assert order.total == Money(3400)
    assert order.shipping == Money(0)


def test_empty_cart(services, make):
    customer, _ = make.customer()
    with pytest.raises(ValidationFailed, match="empty"):
        services.checkout.place_order(customer, make.cart(customer), "tok_visa")


def test_declined_payment_changes_nothing(services, make):
    make.product("TEE")
    customer, _ = make.customer()
    cart_id = make.cart(customer, ("TEE", 1))
    with pytest.raises(PaymentDeclined):
        services.checkout.place_order(customer, cart_id, "tok_decline")
    assert services.orders.list_for_customer(customer) == []
    assert services.carts.get(customer, cart_id).lines


def test_someone_elses_cart(services, make):
    make.product("TEE")
    alice, _ = make.customer()
    bob, _ = make.customer()
    with pytest.raises(NotFound):
        services.checkout.place_order(bob, make.cart(alice, ("TEE", 1)), "tok_visa")
