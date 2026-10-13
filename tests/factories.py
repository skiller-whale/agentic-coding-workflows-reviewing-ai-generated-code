"""Test data. Use these rather than building rows or models by hand."""

import itertools
import sqlite3

from shop import clock
from shop.domain.models import Customer, Product, StaffMember
from shop.domain.money import Money
from shop.repositories.carts import CartRepository
from shop.repositories.customers import CustomerRepository, StaffRepository, TokenRepository
from shop.repositories.products import ProductRepository

_ids = itertools.count(1)


class Factories:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def product(
        self,
        sku: str | None = None,
        price: str = "20.00",
        name: str | None = None,
        category: str = "clothing",
    ) -> Product:
        sku = sku or f"SKU-{next(_ids)}"
        product = Product(
            sku=sku,
            name=name or f"Product {sku}",
            description="",
            category=category,
            price=Money.from_pounds(price),
        )
        ProductRepository(self.conn).add(product)
        return product

    def customer(
        self, loyalty: int = 0, employee_discount: int = 0, email: str | None = None
    ) -> tuple[Customer, str]:
        """A customer and their API token."""
        n = next(_ids)
        repo = CustomerRepository(self.conn)
        customer_id = repo.add(email or f"customer{n}@example.com", f"Customer {n}", clock.now())
        if loyalty:
            repo.adjust_loyalty(customer_id, loyalty)
        if employee_discount:
            repo.set_employee_discount(customer_id, employee_discount)
        token = f"customer-token-{n}"
        TokenRepository(self.conn).add_for_customer(token, customer_id)
        return repo.get(customer_id), token

    def staff(self) -> tuple[StaffMember, str]:
        """A staff member and their API token."""
        n = next(_ids)
        repo = StaffRepository(self.conn)
        staff_id = repo.add(f"staff{n}@shop.example.com", f"Staff {n}")
        token = f"staff-token-{n}"
        TokenRepository(self.conn).add_for_staff(token, staff_id)
        return repo.get(staff_id), token

    def cart(self, customer: Customer, *lines: tuple[str, int]) -> int:
        """A cart for `customer` with (sku, quantity) lines. Returns its id."""
        repo = CartRepository(self.conn)
        cart_id = repo.create(customer.id)
        for sku, quantity in lines:
            repo.set_line(cart_id, sku, quantity)
        return cart_id
