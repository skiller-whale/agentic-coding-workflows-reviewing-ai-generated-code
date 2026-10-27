import os
import sqlite3
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from shop.money import Money
from shop.pricing import Line, Price

DATABASE = os.environ.get("SHOP_DATABASE", "shop.db")
MIGRATIONS = Path(__file__).parent.parent / "migrations"


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    price: Money


@dataclass(frozen=True)
class Order:
    id: int
    lines: list[Line]
    price: Price


def connect(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    migrate(conn)
    return conn


def get_db() -> Iterator[sqlite3.Connection]:
    conn = connect(DATABASE)
    try:
        yield conn
    finally:
        conn.close()


def migrate(conn: sqlite3.Connection) -> None:
    # SQLite's user_version records how many migrations have been run.
    done = conn.execute("PRAGMA user_version").fetchone()[0]
    for number, migration in enumerate(sorted(MIGRATIONS.glob("*.sql")), start=1):
        if number > done:
            conn.executescript(migration.read_text())
            conn.execute(f"PRAGMA user_version = {number}")


def list_products(conn: sqlite3.Connection) -> list[Product]:
    rows = conn.execute("SELECT * FROM products ORDER BY sku")
    return [Product(row["sku"], row["name"], Money(row["price_pence"])) for row in rows]


def get_product(conn: sqlite3.Connection, sku: str) -> Product | None:
    row = conn.execute("SELECT * FROM products WHERE sku = ?", (sku,)).fetchone()
    if row is None:
        return None
    return Product(row["sku"], row["name"], Money(row["price_pence"]))


def add_product(conn: sqlite3.Connection, product: Product) -> None:
    with conn:
        conn.execute(
            "INSERT INTO products (sku, name, price_pence) VALUES (?, ?, ?)",
            (product.sku, product.name, product.price.pence),
        )


def add_order(conn: sqlite3.Connection, lines: list[Line], price: Price) -> int:
    with conn:
        order_id = conn.execute(
            "INSERT INTO orders (subtotal_pence, shipping_pence, total_pence) VALUES (?, ?, ?)",
            (price.subtotal.pence, price.shipping.pence, price.total.pence),
        ).lastrowid
        conn.executemany(
            "INSERT INTO order_lines (order_id, sku, price_pence, quantity) VALUES (?, ?, ?, ?)",
            [(order_id, line.sku, line.price.pence, line.quantity) for line in lines],
        )
    return order_id


def get_order(conn: sqlite3.Connection, order_id: int) -> Order | None:
    row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if row is None:
        return None
    line_rows = conn.execute(
        "SELECT sku, price_pence, quantity FROM order_lines WHERE order_id = ? ORDER BY rowid",
        (order_id,),
    )
    lines = [Line(r["sku"], Money(r["price_pence"]), r["quantity"]) for r in line_rows]
    price = Price(
        subtotal=Money(row["subtotal_pence"]),
        shipping=Money(row["shipping_pence"]),
        total=Money(row["total_pence"]),
    )
    return Order(row["id"], lines, price)
