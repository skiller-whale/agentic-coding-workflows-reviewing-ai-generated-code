from shop.db.connection import transaction
from shop.domain.errors import ValidationFailed
from shop.domain.models import Product, StaffMember
from shop.domain.money import Money
from shop.repositories.products import ProductRepository
from shop.services.audit import AuditLog


class CatalogService:
    def __init__(self, products: ProductRepository, audit: AuditLog):
        self.products = products
        self.audit = audit

    def list_products(self, category: str | None = None) -> list[Product]:
        return self.products.list(category=category)

    def get_product(self, sku: str) -> Product:
        return self.products.get(sku)

    # --- staff ---

    def create_product(
        self,
        staff: StaffMember,
        sku: str,
        name: str,
        category: str,
        price: Money,
        description: str = "",
    ) -> Product:
        if price.pence <= 0:
            raise ValidationFailed("Price must be more than zero")
        product = Product(
            sku=sku, name=name, description=description, category=category, price=price
        )
        with transaction(self.products.conn):
            self.products.add(product)
            self.audit.record(staff, "product.created", f"product:{sku}", price=str(price))
        return product

    def change_price(self, staff: StaffMember, sku: str, price: Money) -> Product:
        if price.pence <= 0:
            raise ValidationFailed("Price must be more than zero")
        with transaction(self.products.conn):
            product = self.products.get(sku)
            updated = Product(**{**product.__dict__, "price": price})
            self.products.update(updated)
            self.audit.record(
                staff,
                "product.price_changed",
                f"product:{sku}",
                old=str(product.price),
                new=str(price),
            )
        return updated
