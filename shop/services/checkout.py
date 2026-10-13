import logging

from shop import clock
from shop.config import Settings
from shop.db.connection import transaction
from shop.domain import loyalty
from shop.domain.employee_discounts import employee_discount
from shop.domain.errors import ValidationFailed
from shop.domain.models import Customer, Order, OrderStatus
from shop.domain.money import Money
from shop.domain.pricing import price
from shop.payments.gateway import PaymentGateway
from shop.repositories.carts import CartRepository
from shop.repositories.customers import CustomerRepository
from shop.repositories.orders import OrderRepository
from shop.services.carts import CartService

log = logging.getLogger(__name__)


class CheckoutService:
    def __init__(
        self,
        carts: CartService,
        cart_repo: CartRepository,
        customers: CustomerRepository,
        orders: OrderRepository,
        gateway: PaymentGateway,
        settings: Settings,
    ):
        self.carts = carts
        self.cart_repo = cart_repo
        self.customers = customers
        self.orders = orders
        self.gateway = gateway
        self.settings = settings

    def place_order(
        self, customer: Customer, cart_id: int, payment_token: str, redeem_points: int = 0
    ) -> Order:
        cart = self.carts.get(customer, cart_id)
        if not cart.lines:
            raise ValidationFailed("Your cart is empty")
        lines = self.carts.order_lines(cart)

        merchandise = Money.sum(line.line_total for line in lines)
        adjustments = []
        staff_discount = employee_discount(merchandise, customer.employee_discount_percent)
        if staff_discount:
            adjustments.append(staff_discount)
        if redeem_points:
            adjustments.append(
                loyalty.redemption(
                    redeem_points,
                    customer.loyalty_balance,
                    merchandise,
                    self.settings.loyalty_point_value,
                    self.settings.loyalty_max_redemption_percent,
                )
            )
        breakdown = price(lines, adjustments, self.settings.free_shipping_threshold)
        points = loyalty.points_earned(
            breakdown.total - breakdown.shipping, self.settings.loyalty_points_per_pound
        )

        with transaction(self.orders.conn):
            payment_ref = self.gateway.charge(breakdown.total, payment_token)
            order = Order(
                id=0,
                customer_id=customer.id,
                status=OrderStatus.PLACED,
                lines=lines,
                adjustments=breakdown.adjustments,
                merchandise=breakdown.merchandise,
                tax=breakdown.tax,
                shipping=breakdown.shipping,
                total=breakdown.total,
                loyalty_points_earned=points,
                loyalty_points_redeemed=redeem_points,
                payment_ref=payment_ref,
                placed_at=clock.now(),
            )
            order_id = self.orders.add(order)
            self.customers.adjust_loyalty(customer.id, points - redeem_points)
            self.cart_repo.delete(cart.id)
            order = self.orders.get(order_id)

        log.info("Order %s placed by customer %s for %s", order.id, customer.id, order.total)
        return order
