from shop import clock
from shop.domain.models import AuditEntry, StaffMember
from shop.repositories.audit import AuditRepository


class AuditLog:
    """A record of every change staff make, for support and compliance."""

    def __init__(self, repo: AuditRepository):
        self.repo = repo

    def record(self, staff: StaffMember, action: str, subject: str, **details) -> None:
        self.repo.add(staff.id, action, subject, details, clock.now())

    def entries(self, subject: str | None = None, limit: int = 100) -> list[AuditEntry]:
        return self.repo.list(subject=subject, limit=limit)
