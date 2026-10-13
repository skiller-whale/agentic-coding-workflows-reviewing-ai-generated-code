from fastapi import APIRouter, Depends

from shop.api.deps import get_services, require_staff
from shop.api.schemas.admin import PriceIn, ProductIn
from shop.api.schemas.catalog import ProductOut
from shop.api.schemas.common import parse_money
from shop.domain.models import StaffMember
from shop.services import Services

router = APIRouter(prefix="/products")


@router.post("", status_code=201)
def create_product(
    body: ProductIn,
    staff: StaffMember = Depends(require_staff),
    services: Services = Depends(get_services),
) -> ProductOut:
    product = services.catalog.create_product(
        staff, body.sku, body.name, body.category, parse_money(body.price), body.description
    )
    return ProductOut.of(product)


@router.put("/{sku}/price")
def change_price(
    sku: str,
    body: PriceIn,
    staff: StaffMember = Depends(require_staff),
    services: Services = Depends(get_services),
) -> ProductOut:
    return ProductOut.of(services.catalog.change_price(staff, sku, parse_money(body.price)))
