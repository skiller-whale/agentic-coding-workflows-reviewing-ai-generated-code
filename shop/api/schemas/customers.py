from pydantic import BaseModel

from shop.domain.models import Customer


class RegisterIn(BaseModel):
    email: str
    name: str


class CustomerOut(BaseModel):
    id: int
    email: str
    name: str
    loyalty_balance: int
    employee_discount_percent: int

    @classmethod
    def of(cls, customer: Customer) -> "CustomerOut":
        return cls(
            id=customer.id,
            email=customer.email,
            name=customer.name,
            loyalty_balance=customer.loyalty_balance,
            employee_discount_percent=customer.employee_discount_percent,
        )


class RegisteredOut(BaseModel):
    customer: CustomerOut
    token: str
