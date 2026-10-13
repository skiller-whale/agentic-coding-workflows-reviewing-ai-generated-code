from fastapi import APIRouter, Depends

from shop.api.deps import get_services
from shop.api.schemas.catalog import ProductOut
from shop.services import Services

router = APIRouter(prefix="/products", tags=["catalog"])


@router.get("")
def list_products(
    category: str | None = None, services: Services = Depends(get_services)
) -> list[ProductOut]:
    return [ProductOut.of(product) for product in services.catalog.list_products(category)]


@router.get("/{sku}")
def get_product(sku: str, services: Services = Depends(get_services)) -> ProductOut:
    return ProductOut.of(services.catalog.get_product(sku))
