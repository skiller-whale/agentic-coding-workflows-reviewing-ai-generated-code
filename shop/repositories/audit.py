import json

from shop.domain.models import AuditEntry
from shop.repositories.base import Repository, from_db_time, to_db_time


class AuditRepository(Repository):
    def add(self, staff_id: int, action: str, subject: str, details: dict, created_at) -> int:
        return self.conn.execute(
            "INSERT INTO audit_log (staff_id, action, subject, details, created_at)"
            " VALUES (?, ?, ?, ?, ?)",
            (
                staff_id,
                action,
                subject,
                json.dumps(details, sort_keys=True),
                to_db_time(created_at),
            ),
        ).lastrowid

    def list(self, subject: str | None = None, limit: int = 100) -> list[AuditEntry]:
        query = "SELECT * FROM audit_log"
        params: list = []
        if subject is not None:
            query += " WHERE subject = ?"
            params.append(subject)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        return [
            AuditEntry(
                id=row["id"],
                staff_id=row["staff_id"],
                action=row["action"],
                subject=row["subject"],
                details=json.loads(row["details"]),
                created_at=from_db_time(row["created_at"]),
            )
            for row in self.conn.execute(query, params)
        ]
