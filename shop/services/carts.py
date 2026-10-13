from shop.config import Settings
from shop.domain.errors import NotFound, ValidationFailed
from shop.domain.models import Cart, Customer, OrderLine
from shop.domain.pricing import PriceBreakdown, price
from shop.repositories.carts import CartRepository
from shop.repositories.products import ProductRepository

MAX_QUANTITY = 20


class CartService:
    def __init__(self, carts: CartRepository, products: ProductRepository, settings: Settings):
        self.carts = carts
        self.products = products
        self.settings = settings

    def create(self, customer: Customer) -> Cart:
        return self.carts.get(self.carts.create(customer.id))

    def get(self, customer: Customer, cart_id: int) -> Cart:
        cart = self.carts.get(cart_id)
        if cart.customer_id != customer.id:
            # Don't reveal that someone else's cart exists.
            raise NotFound(f"No cart {cart_id}")
        return cart

    def set_quantity(self, customer: Customer, cart_id: int, sku: str, quantity: int) -> Cart:
        cart = self.get(customer, cart_id)
        if quantity == 0:
            self.carts.remove_line(cart.id, sku)
            return self.carts.get(cart.id)
        if not 1 <= quantity <= MAX_QUANTITY:
            raise ValidationFailed(f"Quantity must be between 1 and {MAX_QUANTITY}")
        self.products.get(sku)
        self.carts.set_line(cart.id, sku, quantity)
        return self.carts.get(cart.id)

    def order_lines(self, cart: Cart) -> list[OrderLine]:
        lines = []
        for cart_line in cart.lines:
            product = self.products.get(cart_line.sku)
            lines.append(
                OrderLine(
                    sku=product.sku,
                    name=product.name,
                    unit_price=product.price,
                    quantity=cart_line.quantity,
                )
            )
        return lines

    def preview(self, customer: Customer, cart_id: int) -> PriceBreakdown:
        """What the cart would cost if the customer checked out now."""
        cart = self.get(customer, cart_id)
        return price(self.order_lines(cart), [], self.settings.free_shipping_threshold)
