from datetime import datetime

from shop.domain.errors import NotFound
from shop.domain.models import Adjustment, Order, OrderLine, OrderStatus
from shop.domain.money import Money
from shop.repositories.base import Repository, from_db_time, to_db_time


class OrderRepository(Repository):
    def add(self, order: Order) -> int:
        """Save a new order (ignoring `order.id`) and return its id."""
        order_id = self.conn.execute(
            "INSERT INTO orders (customer_id, status, merchandise_pence, tax_pence,"
            " shipping_pence, total_pence, loyalty_points_earned, loyalty_points_redeemed,"
            " payment_ref, placed_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                order.customer_id,
                order.status.value,
                order.merchandise.pence,
                order.tax.pence,
                order.shipping.pence,
                order.total.pence,
                order.loyalty_points_earned,
                order.loyalty_points_redeemed,
                order.payment_ref,
                to_db_time(order.placed_at),
            ),
        ).lastrowid
        self.conn.executemany(
            "INSERT INTO order_lines (order_id, position, sku, name, unit_price_pence, quantity)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            [
                (order_id, position, line.sku, line.name, line.unit_price.pence, line.quantity)
                for position, line in enumerate(order.lines)
            ],
        )
        self.conn.executemany(
            "INSERT INTO order_adjustments (order_id, position, kind, description, amount_pence)"
            " VALUES (?, ?, ?, ?, ?)",
            [
                (order_id, position, adj.kind, adj.description, adj.amount.pence)
                for position, adj in enumerate(order.adjustments)
            ],
        )
        return order_id

    def get(self, order_id: int) -> Order:
        row = self.conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        if row is None:
            raise NotFound(f"No order {order_id}")
        return self._order(row)

    def list_for_customer(self, customer_id: int) -> list[Order]:
        rows = self.conn.execute(
            "SELECT * FROM orders WHERE customer_id = ? ORDER BY placed_at DESC, id DESC",
            (customer_id,),
        )
        return [self._order(row) for row in rows.fetchall()]

    def set_status(
        self, order_id: int, status: OrderStatus, dispatched_at: datetime | None = None
    ) -> None:
        self.get(order_id)
        self.conn.execute(
            "UPDATE orders SET status = ?, dispatched_at = COALESCE(?, dispatched_at) WHERE id = ?",
            (status.value, to_db_time(dispatched_at), order_id),
        )

    def _order(self, row) -> Order:
        lines = [
            OrderLine(
                sku=line["sku"],
                name=line["name"],
                unit_price=Money(line["unit_price_pence"]),
                quantity=line["quantity"],
            )
            for line in self.conn.execute(
                "SELECT * FROM order_lines WHERE order_id = ? ORDER BY position", (row["id"],)
            )
        ]
        adjustments = [
            Adjustment(
                kind=adj["kind"], description=adj["description"], amount=Money(adj["amount_pence"])
            )
            for adj in self.conn.execute(
                "SELECT * FROM order_adjustments WHERE order_id = ? ORDER BY position",
                (row["id"],),
            )
        ]
        return Order(
            id=row["id"],
            customer_id=row["customer_id"],
            status=OrderStatus(row["status"]),
            lines=lines,
            adjustments=adjustments,
            merchandise=Money(row["merchandise_pence"]),
            tax=Money(row["tax_pence"]),
            shipping=Money(row["shipping_pence"]),
            total=Money(row["total_pence"]),
            loyalty_points_earned=row["loyalty_points_earned"],
            loyalty_points_redeemed=row["loyalty_points_redeemed"],
            payment_ref=row["payment_ref"],
            placed_at=from_db_time(row["placed_at"]),
            dispatched_at=from_db_time(row["dispatched_at"]),
        )
