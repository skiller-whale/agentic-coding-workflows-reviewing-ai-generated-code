import hashlib
import sqlite3
from pathlib import Path

MIGRATIONS = Path(__file__).parent / "migrations"


def migration_files() -> list[Path]:
    return sorted(MIGRATIONS.glob("[0-9][0-9][0-9]_*.sql"))


def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def migrate(conn: sqlite3.Connection) -> list[str]:
    """Apply any migrations that haven't been applied yet. Returns the names applied."""
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations ("
        " name TEXT PRIMARY KEY, checksum TEXT NOT NULL, applied_at TEXT NOT NULL"
        " DEFAULT CURRENT_TIMESTAMP)"
    )
    applied = {
        row["name"]: row["checksum"]
        for row in conn.execute("SELECT name, checksum FROM schema_migrations")
    }
    newly_applied = []
    for path in migration_files():
        if path.name in applied:
            if applied[path.name] != checksum(path):
                raise RuntimeError(f"Migration {path.name} has changed since it was applied")
            continue
        conn.executescript(path.read_text())
        conn.execute(
            "INSERT INTO schema_migrations (name, checksum) VALUES (?, ?)",
            (path.name, checksum(path)),
        )
        newly_applied.append(path.name)
    return newly_applied
