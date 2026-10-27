import os

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException

from shop import db
from shop.db import get_db
from shop.money import Money
from shop.pricing import Line, price
from shop.schemas import Checkout, NewProduct, order_json, price_json, product_json

STAFF_API_KEY = os.environ.get("SHOP_STAFF_API_KEY", "staff-secret")


def require_staff(x_api_key: str | None = Header(default=None)) -> None:
    if x_api_key != STAFF_API_KEY:
        raise HTTPException(401, "Staff only")


app = FastAPI(title="Shop")
admin = APIRouter(prefix="/admin", dependencies=[Depends(require_staff)])


@app.get("/products")
def list_products(conn=Depends(get_db)):
    return [product_json(product) for product in db.list_products(conn)]


@app.post("/checkout", status_code=201)
def checkout(body: Checkout, conn=Depends(get_db)):
    lines = []
    for item in body.items:
        product = db.get_product(conn, item.sku)
        if product is None:
            raise HTTPException(422, f"Unknown product: {item.sku}")
        lines.append(Line(product.sku, product.price, item.quantity))
    order_price = price(lines)
    order_id = db.add_order(conn, lines, order_price)
    return {"order_id": order_id, **price_json(order_price)}


@admin.post("/products", status_code=201)
def add_product(body: NewProduct, conn=Depends(get_db)):
    if db.get_product(conn, body.sku):
        raise HTTPException(409, f"Product already exists: {body.sku}")
    product = db.Product(body.sku, body.name, Money.parse(body.price))
    db.add_product(conn, product)
    return product_json(product)


@admin.get("/orders/{order_id}")
def get_order(order_id: int, conn=Depends(get_db)):
    order = db.get_order(conn, order_id)
    if order is None:
        raise HTTPException(404, "No such order")
    return order_json(order)


app.include_router(admin)
