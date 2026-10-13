from shop import clock
from shop.db.connection import transaction
from shop.domain.errors import Conflict, NotFound
from shop.domain.models import Customer, Order, OrderStatus, StaffMember
from shop.payments.gateway import PaymentGateway
from shop.repositories.customers import CustomerRepository
from shop.repositories.orders import OrderRepository
from shop.services.audit import AuditLog


class OrderService:
    def __init__(
        self,
        orders: OrderRepository,
        customers: CustomerRepository,
        audit: AuditLog,
        gateway: PaymentGateway,
    ):
        self.orders = orders
        self.customers = customers
        self.audit = audit
        self.gateway = gateway

    def get_for_customer(self, customer: Customer, order_id: int) -> Order:
        order = self.orders.get(order_id)
        if order.customer_id != customer.id:
            raise NotFound(f"No order {order_id}")
        return order

    def list_for_customer(self, customer: Customer) -> list[Order]:
        return self.orders.list_for_customer(customer.id)

    def cancel(self, customer: Customer, order_id: int) -> Order:
        """Customers can cancel an order until it's dispatched, for a full refund."""
        order = self.get_for_customer(customer, order_id)
        if order.status != OrderStatus.PLACED:
            raise Conflict(f"Order {order_id} has been {order.status.value}, so can't be cancelled")
        with transaction(self.orders.conn):
            self.gateway.refund(order.payment_ref, order.total)
            self.customers.adjust_loyalty(
                customer.id, order.loyalty_points_redeemed - order.loyalty_points_earned
            )
            self.orders.set_status(order.id, OrderStatus.CANCELLED)
            order = self.orders.get(order.id)
        return order

    # --- staff ---

    def get(self, order_id: int) -> Order:
        return self.orders.get(order_id)

    def mark_dispatched(self, staff: StaffMember, order_id: int) -> Order:
        with transaction(self.orders.conn):
            order = self.orders.get(order_id)
            if order.status != OrderStatus.PLACED:
                raise Conflict(f"Order {order_id} is {order.status.value}, not placed")
            self.orders.set_status(order.id, OrderStatus.DISPATCHED, dispatched_at=clock.now())
            order = self.orders.get(order.id)
            self.audit.record(staff, "order.dispatched", f"order:{order.id}")
        return order
