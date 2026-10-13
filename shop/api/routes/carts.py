from fastapi import APIRouter, Depends

from shop.api.deps import current_customer, get_services
from shop.api.schemas.carts import CartLineIn, CartOut
from shop.domain.models import Customer
from shop.services import Services

router = APIRouter(prefix="/carts", tags=["carts"])


def _cart_out(services: Services, customer: Customer, cart_id: int) -> CartOut:
    cart = services.carts.get(customer, cart_id)
    return CartOut.of(cart, services.carts.preview(customer, cart_id))


@router.post("", status_code=201)
def create_cart(
    customer: Customer = Depends(current_customer), services: Services = Depends(get_services)
) -> CartOut:
    cart = services.carts.create(customer)
    return _cart_out(services, customer, cart.id)


@router.get("/{cart_id}")
def get_cart(
    cart_id: int,
    customer: Customer = Depends(current_customer),
    services: Services = Depends(get_services),
) -> CartOut:
    return _cart_out(services, customer, cart_id)


@router.put("/{cart_id}/lines/{sku}")
def set_line(
    cart_id: int,
    sku: str,
    body: CartLineIn,
    customer: Customer = Depends(current_customer),
    services: Services = Depends(get_services),
) -> CartOut:
    services.carts.set_quantity(customer, cart_id, sku, body.quantity)
    return _cart_out(services, customer, cart_id)
