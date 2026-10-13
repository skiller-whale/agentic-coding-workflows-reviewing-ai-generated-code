from fastapi import APIRouter, Depends

from shop.api.deps import get_services, require_staff
from shop.api.schemas.admin import EmployeeDiscountIn
from shop.api.schemas.customers import CustomerOut
from shop.domain.models import StaffMember
from shop.services import Services

router = APIRouter(prefix="/customers")


@router.put("/{customer_id}/employee-discount")
def set_employee_discount(
    customer_id: int,
    body: EmployeeDiscountIn,
    staff: StaffMember = Depends(require_staff),
    services: Services = Depends(get_services),
) -> CustomerOut:
    customer = services.customers.set_employee_discount(staff, customer_id, body.percent)
    return CustomerOut.of(customer)
