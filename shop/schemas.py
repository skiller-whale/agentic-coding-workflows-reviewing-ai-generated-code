from pydantic import BaseModel, Field

from shop.db import Order, Product
from shop.pricing import Price


class Item(BaseModel):
    sku: str
    quantity: int = Field(gt=0)


class Checkout(BaseModel):
    items: list[Item] = Field(min_length=1)


class NewProduct(BaseModel):
    sku: str
    name: str
    price: str = Field(pattern=r"^\d+\.\d\d$")


def product_json(product: Product) -> dict:
    return {"sku": product.sku, "name": product.name, "price": str(product.price)}


def price_json(order_price: Price) -> dict:
    return {
        "subtotal": str(order_price.subtotal),
        "shipping": str(order_price.shipping),
        "total": str(order_price.total),
    }


def order_json(order: Order) -> dict:
    return {
        "id": order.id,
        "items": [
            {"sku": line.sku, "price": str(line.price), "quantity": line.quantity}
            for line in order.lines
        ],
        **price_json(order.price),
    }
