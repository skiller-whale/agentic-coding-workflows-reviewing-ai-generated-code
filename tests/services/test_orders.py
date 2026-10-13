import pytest

from shop.domain.errors import Conflict, NotFound
from shop.domain.models import OrderStatus


@pytest.fixture
def placed(services, make):
    make.product("TEE", price="20.00")
    customer, _ = make.customer(loyalty=100)
    cart_id = make.cart(customer, ("TEE", 2))
    order = services.checkout.place_order(customer, cart_id, "tok_visa", redeem_points=100)
    return customer, order


def test_customer_sees_own_orders(services, make, placed):
    customer, order = placed
    assert services.orders.get_for_customer(customer, order.id) == order
    other, _ = make.customer()
    with pytest.raises(NotFound):
        services.orders.get_for_customer(other, order.id)


def test_cancel_refunds_and_reverses_loyalty(services, gateway, placed):
    customer, order = placed
    cancelled = services.orders.cancel(customer, order.id)
    assert cancelled.status == OrderStatus.CANCELLED
    assert gateway.refunds == [(order.payment_ref, order.total)]
    assert services.customers.get(customer.id).loyalty_balance == 100


def test_cannot_cancel_after_dispatch(services, make, placed):
    customer, order = placed
    staff, _ = make.staff()
    services.orders.mark_dispatched(staff, order.id)
    with pytest.raises(Conflict):
        services.orders.cancel(customer, order.id)


def test_dispatch_is_audited(services, make, placed, frozen_clock):
    _, order = placed
    staff, _ = make.staff()
    dispatched = services.orders.mark_dispatched(staff, order.id)
    assert dispatched.dispatched_at == frozen_clock
    [entry] = services.audit.entries(subject=f"order:{order.id}")
    assert (entry.staff_id, entry.action) == (staff.id, "order.dispatched")
