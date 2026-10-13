from pydantic import BaseModel, Field, field_validator

from shop.api.schemas.common import check_money
from shop.domain.models import AuditEntry


class ProductIn(BaseModel):
    sku: str = Field(pattern=r"^[A-Z0-9-]{2,20}$")
    name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    price: str
    description: str = ""

    @field_validator("price")
    @classmethod
    def _check_price(cls, value: str) -> str:
        return check_money(value)


class PriceIn(BaseModel):
    price: str

    @field_validator("price")
    @classmethod
    def _check_price(cls, value: str) -> str:
        return check_money(value)


class EmployeeDiscountIn(BaseModel):
    percent: int


class AuditEntryOut(BaseModel):
    id: int
    staff_id: int
    action: str
    subject: str
    details: dict
    created_at: str

    @classmethod
    def of(cls, entry: AuditEntry) -> "AuditEntryOut":
        return cls(
            id=entry.id,
            staff_id=entry.staff_id,
            action=entry.action,
            subject=entry.subject,
            details=entry.details,
            created_at=entry.created_at.isoformat(),
        )
