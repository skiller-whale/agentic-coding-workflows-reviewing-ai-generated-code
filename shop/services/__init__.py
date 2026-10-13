import sqlite3
from dataclasses import dataclass

from shop.config import Settings
from shop.payments.gateway import PaymentGateway
from shop.repositories.audit import AuditRepository
from shop.repositories.carts import CartRepository
from shop.repositories.customers import CustomerRepository, StaffRepository, TokenRepository
from shop.repositories.orders import OrderRepository
from shop.repositories.products import ProductRepository
from shop.services.audit import AuditLog
from shop.services.carts import CartService
from shop.services.catalog import CatalogService
from shop.services.checkout import CheckoutService
from shop.services.customers import CustomerService
from shop.services.orders import OrderService


@dataclass
class Services:
    """Everything the API needs, wired to one database connection."""

    settings: Settings
    catalog: CatalogService
    customers: CustomerService
    carts: CartService
    checkout: CheckoutService
    orders: OrderService
    audit: AuditLog
    staff: StaffRepository
    tokens: TokenRepository

    @classmethod
    def build(
        cls, conn: sqlite3.Connection, settings: Settings, gateway: PaymentGateway
    ) -> "Services":
        products = ProductRepository(conn)
        customers = CustomerRepository(conn)
        tokens = TokenRepository(conn)
        cart_repo = CartRepository(conn)
        orders = OrderRepository(conn)
        audit = AuditLog(AuditRepository(conn))
        carts = CartService(cart_repo, products, settings)
        return cls(
            settings=settings,
            catalog=CatalogService(products, audit),
            customers=CustomerService(customers, tokens, audit),
            carts=carts,
            checkout=CheckoutService(carts, cart_repo, customers, orders, gateway, settings),
            orders=OrderService(orders, customers, audit, gateway),
            audit=audit,
            staff=StaffRepository(conn),
            tokens=tokens,
        )
