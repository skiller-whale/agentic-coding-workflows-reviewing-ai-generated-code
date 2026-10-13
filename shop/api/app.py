import sqlite3

from fastapi import FastAPI

from shop.api import errors
from shop.api.routes import admin, carts, catalog, customers, orders
from shop.config import Settings, load_settings
from shop.db.connection import connect
from shop.db.migrate import migrate
from shop.payments.gateway import FakeGateway, PaymentGateway
from shop.services import Services


def create_app(
    settings: Settings | None = None,
    conn: sqlite3.Connection | None = None,
    gateway: PaymentGateway | None = None,
) -> FastAPI:
    settings = settings or load_settings()
    if conn is None:
        conn = connect(settings.database)
        migrate(conn)

    app = FastAPI(title="shop", version="0.7.0")
    app.state.services = Services.build(conn, settings, gateway or FakeGateway())
    errors.install(app)

    app.include_router(catalog.router)
    app.include_router(customers.router)
    app.include_router(carts.router)
    app.include_router(orders.router)
    app.include_router(admin.router)
    return app


app = create_app()
