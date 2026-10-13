from fastapi import APIRouter, Depends

from shop.api.deps import current_customer, get_services
from shop.api.schemas.customers import CustomerOut, RegisteredOut, RegisterIn
from shop.domain.models import Customer
from shop.services import Services

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", status_code=201)
def register(body: RegisterIn, services: Services = Depends(get_services)) -> RegisteredOut:
    customer, token = services.customers.register(body.email, body.name)
    return RegisteredOut(customer=CustomerOut.of(customer), token=token)


@router.get("/me")
def me(customer: Customer = Depends(current_customer)) -> CustomerOut:
    return CustomerOut.of(customer)
