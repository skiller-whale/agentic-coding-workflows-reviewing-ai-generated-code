from shop.domain.errors import NotFound
from shop.domain.models import Cart, CartLine
from shop.repositories.base import Repository


class CartRepository(Repository):
    def create(self, customer_id: int) -> int:
        return self.conn.execute(
            "INSERT INTO carts (customer_id) VALUES (?)", (customer_id,)
        ).lastrowid

    def get(self, cart_id: int) -> Cart:
        row = self.conn.execute("SELECT * FROM carts WHERE id = ?", (cart_id,)).fetchone()
        if row is None:
            raise NotFound(f"No cart {cart_id}")
        lines = [
            CartLine(sku=line["sku"], quantity=line["quantity"])
            for line in self.conn.execute(
                "SELECT sku, quantity FROM cart_lines WHERE cart_id = ? ORDER BY rowid", (cart_id,)
            )
        ]
        return Cart(id=row["id"], customer_id=row["customer_id"], lines=lines)

    def set_line(self, cart_id: int, sku: str, quantity: int) -> None:
        self.conn.execute(
            "INSERT INTO cart_lines (cart_id, sku, quantity) VALUES (?, ?, ?)"
            " ON CONFLICT (cart_id, sku) DO UPDATE SET quantity = excluded.quantity",
            (cart_id, sku, quantity),
        )

    def remove_line(self, cart_id: int, sku: str) -> None:
        self.conn.execute("DELETE FROM cart_lines WHERE cart_id = ? AND sku = ?", (cart_id, sku))

    def delete(self, cart_id: int) -> None:
        self.conn.execute("DELETE FROM carts WHERE id = ?", (cart_id,))
