from fastapi import APIRouter, Depends

from shop.api.deps import current_customer, get_services
from shop.api.schemas.orders import CheckoutIn, OrderOut
from shop.domain.models import Customer
from shop.services import Services

router = APIRouter(tags=["orders"])


@router.post("/checkout", status_code=201)
def checkout(
    body: CheckoutIn,
    customer: Customer = Depends(current_customer),
    services: Services = Depends(get_services),
) -> OrderOut:
    order = services.checkout.place_order(
        customer, body.cart_id, body.payment_token, redeem_points=body.redeem_points
    )
    return OrderOut.of(order)


@router.get("/orders")
def list_orders(
    customer: Customer = Depends(current_customer), services: Services = Depends(get_services)
) -> list[OrderOut]:
    return [OrderOut.of(order) for order in services.orders.list_for_customer(customer)]


@router.get("/orders/{order_id}")
def get_order(
    order_id: int,
    customer: Customer = Depends(current_customer),
    services: Services = Depends(get_services),
) -> OrderOut:
    return OrderOut.of(services.orders.get_for_customer(customer, order_id))


@router.post("/orders/{order_id}/cancel")
def cancel_order(
    order_id: int,
    customer: Customer = Depends(current_customer),
    services: Services = Depends(get_services),
) -> OrderOut:
    return OrderOut.of(services.orders.cancel(customer, order_id))
