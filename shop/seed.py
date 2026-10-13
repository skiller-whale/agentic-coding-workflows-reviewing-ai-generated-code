"""Demo data for running the shop locally: `uv run python -m shop.seed shop.db`."""

import sys

from shop.db.connection import connect
from shop.db.migrate import migrate
from shop.domain.models import Product
from shop.domain.money import Money
from shop.repositories.customers import StaffRepository, TokenRepository
from shop.repositories.products import ProductRepository

PRODUCTS = [
    Product("MUG", "Enamel mug", "Speckled enamel, 350ml.", "kitchen", Money(1000)),
    Product("TEE", "Organic cotton tee", "Heavyweight, boxy fit.", "clothing", Money(2000)),
    Product("BEANIE", "Merino beanie", "Ribbed, one size.", "clothing", Money(1565)),
    Product("HOODIE", "Heavyweight hoodie", "Brushed-back fleece.", "clothing", Money(5500)),
    Product("JACKET", "Waxed jacket", "Waxed cotton, tartan lining.", "clothing", Money(10000)),
    Product("TOTE", "Canvas tote", "Natural canvas, long handles.", "bags", Money(1200)),
]


def seed(database: str) -> None:
    conn = connect(database)
    migrate(conn)
    products = ProductRepository(conn)
    for product in PRODUCTS:
        products.add(product)
    staff_id = StaffRepository(conn).add("sam@shop.example.com", "Sam")
    TokenRepository(conn).add_for_staff("staff-demo-token", staff_id)


if __name__ == "__main__":
    seed(sys.argv[1] if len(sys.argv) > 1 else "shop.db")
