import sqlite3
from datetime import UTC, datetime


class Repository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn


def to_db_time(value: datetime | None) -> str | None:
    """Times are stored as UTC ISO 8601 strings, so they sort and compare correctly."""
    return value.astimezone(UTC).isoformat() if value is not None else None


def from_db_time(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value is not None else None
