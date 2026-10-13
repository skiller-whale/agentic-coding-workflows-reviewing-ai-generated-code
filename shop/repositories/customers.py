from shop.domain.errors import Conflict, NotFound, ValidationFailed
from shop.domain.models import Customer, StaffMember
from shop.repositories.base import Repository, from_db_time, to_db_time


def _customer(row) -> Customer:
    return Customer(
        id=row["id"],
        email=row["email"],
        name=row["name"],
        loyalty_balance=row["loyalty_balance"],
        created_at=from_db_time(row["created_at"]),
        employee_discount_percent=row["employee_discount_percent"],
    )


class CustomerRepository(Repository):
    def get(self, customer_id: int) -> Customer:
        row = self.conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
        if row is None:
            raise NotFound(f"No customer {customer_id}")
        return _customer(row)

    def add(self, email: str, name: str, created_at) -> int:
        if self.conn.execute("SELECT 1 FROM customers WHERE email = ?", (email,)).fetchone():
            raise Conflict(f"There's already an account for {email}")
        cursor = self.conn.execute(
            "INSERT INTO customers (email, name, created_at) VALUES (?, ?, ?)",
            (email, name, to_db_time(created_at)),
        )
        return cursor.lastrowid

    def set_employee_discount(self, customer_id: int, percent: int) -> None:
        self.get(customer_id)
        self.conn.execute(
            "UPDATE customers SET employee_discount_percent = ? WHERE id = ?",
            (percent, customer_id),
        )

    def adjust_loyalty(self, customer_id: int, delta: int) -> int:
        balance = self.get(customer_id).loyalty_balance
        if balance + delta < 0:
            raise ValidationFailed(f"Only {balance} loyalty points available")
        self.conn.execute(
            "UPDATE customers SET loyalty_balance = loyalty_balance + ? WHERE id = ?",
            (delta, customer_id),
        )
        return balance + delta


class StaffRepository(Repository):
    def get(self, staff_id: int) -> StaffMember:
        row = self.conn.execute("SELECT * FROM staff WHERE id = ?", (staff_id,)).fetchone()
        if row is None:
            raise NotFound(f"No staff member {staff_id}")
        return StaffMember(id=row["id"], email=row["email"], name=row["name"])

    def add(self, email: str, name: str) -> int:
        cursor = self.conn.execute("INSERT INTO staff (email, name) VALUES (?, ?)", (email, name))
        return cursor.lastrowid


class TokenRepository(Repository):
    def add_for_customer(self, token: str, customer_id: int) -> None:
        self.conn.execute(
            "INSERT INTO api_tokens (token, customer_id) VALUES (?, ?)", (token, customer_id)
        )

    def add_for_staff(self, token: str, staff_id: int) -> None:
        self.conn.execute(
            "INSERT INTO api_tokens (token, staff_id) VALUES (?, ?)", (token, staff_id)
        )

    def resolve(self, token: str) -> tuple[str, int] | None:
        """("customer", id) or ("staff", id) for a token, or None if it isn't one."""
        row = self.conn.execute(
            "SELECT customer_id, staff_id FROM api_tokens WHERE token = ?", (token,)
        ).fetchone()
        if row is None:
            return None
        if row["customer_id"] is not None:
            return ("customer", row["customer_id"])
        return ("staff", row["staff_id"])
