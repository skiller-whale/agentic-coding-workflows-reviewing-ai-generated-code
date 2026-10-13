from shop.domain.errors import Conflict, NotFound
from shop.domain.models import Product
from shop.domain.money import Money
from shop.repositories.base import Repository


def _product(row) -> Product:
    return Product(
        sku=row["sku"],
        name=row["name"],
        description=row["description"],
        category=row["category"],
        price=Money(row["price_pence"]),
    )


class ProductRepository(Repository):
    def get(self, sku: str) -> Product:
        row = self.conn.execute("SELECT * FROM products WHERE sku = ?", (sku,)).fetchone()
        if row is None:
            raise NotFound(f"No product {sku!r}")
        return _product(row)

    def list(self, category: str | None = None) -> list[Product]:
        query = "SELECT * FROM products"
        params: list = []
        if category is not None:
            query += " WHERE category = ?"
            params.append(category)
        query += " ORDER BY category, name"
        return [_product(row) for row in self.conn.execute(query, params)]

    def add(self, product: Product) -> None:
        if self.conn.execute("SELECT 1 FROM products WHERE sku = ?", (product.sku,)).fetchone():
            raise Conflict(f"There's already a product {product.sku!r}")
        self.conn.execute(
            "INSERT INTO products (sku, name, description, category, price_pence)"
            " VALUES (?, ?, ?, ?, ?)",
            (product.sku, product.name, product.description, product.category, product.price.pence),
        )

    def update(self, product: Product) -> None:
        self.get(product.sku)
        self.conn.execute(
            "UPDATE products SET name = ?, description = ?, category = ?, price_pence = ?"
            " WHERE sku = ?",
            (product.name, product.description, product.category, product.price.pence, product.sku),
        )
