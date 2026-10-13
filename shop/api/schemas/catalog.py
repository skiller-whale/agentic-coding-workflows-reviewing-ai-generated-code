from pydantic import BaseModel

from shop.api.schemas.common import money
from shop.domain.models import Product


class ProductOut(BaseModel):
    sku: str
    name: str
    description: str
    category: str
    price: str

    @classmethod
    def of(cls, product: Product) -> "ProductOut":
        return cls(
            sku=product.sku,
            name=product.name,
            description=product.description,
            category=product.category,
            price=money(product.price),
        )
