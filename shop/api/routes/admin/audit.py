from fastapi import APIRouter, Depends, Query

from shop.api.deps import get_services
from shop.api.schemas.admin import AuditEntryOut
from shop.services import Services

router = APIRouter(prefix="/audit")


@router.get("")
def list_entries(
    subject: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    services: Services = Depends(get_services),
) -> list[AuditEntryOut]:
    return [AuditEntryOut.of(entry) for entry in services.audit.entries(subject, limit)]
