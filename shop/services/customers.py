import secrets

from shop import clock
from shop.db.connection import transaction
from shop.domain.employee_discounts import check_percent
from shop.domain.errors import ValidationFailed
from shop.domain.models import Customer, StaffMember
from shop.repositories.customers import CustomerRepository, TokenRepository
from shop.services.audit import AuditLog


class CustomerService:
    def __init__(self, customers: CustomerRepository, tokens: TokenRepository, audit: AuditLog):
        self.customers = customers
        self.tokens = tokens
        self.audit = audit

    def register(self, email: str, name: str) -> tuple[Customer, str]:
        """Create an account, returning the customer and an API token for them."""
        if "@" not in email:
            raise ValidationFailed("That doesn't look like an email address")
        with transaction(self.customers.conn):
            customer_id = self.customers.add(email.strip().lower(), name.strip(), clock.now())
            token = secrets.token_urlsafe(24)
            self.tokens.add_for_customer(token, customer_id)
        return self.customers.get(customer_id), token

    def get(self, customer_id: int) -> Customer:
        return self.customers.get(customer_id)

    # --- staff ---

    def set_employee_discount(self, staff: StaffMember, customer_id: int, percent: int) -> Customer:
        """Give a staff member's customer account a percentage off everything they buy."""
        check_percent(percent)
        with transaction(self.customers.conn):
            old = self.customers.get(customer_id).employee_discount_percent
            self.customers.set_employee_discount(customer_id, percent)
            self.audit.record(
                staff,
                "customer.employee_discount_changed",
                f"customer:{customer_id}",
                old=old,
                new=percent,
            )
        return self.customers.get(customer_id)
