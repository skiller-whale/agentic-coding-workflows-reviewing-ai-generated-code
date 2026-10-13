from fastapi import APIRouter, Depends

from shop.api.deps import get_services, require_staff
from shop.api.schemas.orders import OrderOut
from shop.domain.models import StaffMember
from shop.services import Services

router = APIRouter(prefix="/orders")


@router.get("/{order_id}")
def get_order(order_id: int, services: Services = Depends(get_services)) -> OrderOut:
    return OrderOut.of(services.orders.get(order_id))


@router.post("/{order_id}/dispatch")
def dispatch(
    order_id: int,
    staff: StaffMember = Depends(require_staff),
    services: Services = Depends(get_services),
) -> OrderOut:
    return OrderOut.of(services.orders.mark_dispatched(staff, order_id))
