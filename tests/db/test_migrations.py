import pytest

from shop.db.connection import connect, transaction
from shop.db.migrate import migrate, migration_files


def test_migrations_apply_in_order():
    conn = connect()
    applied = migrate(conn)
    assert applied == [path.name for path in migration_files()]
    assert migrate(conn) == []


def test_migration_numbers_are_unique():
    numbers = [path.name[:3] for path in migration_files()]
    assert len(numbers) == len(set(numbers))


def test_changed_migration_is_refused(tmp_path, monkeypatch):
    from shop.db import migrate as migrate_module

    for path in migration_files():
        (tmp_path / path.name).write_text(path.read_text())
    monkeypatch.setattr(migrate_module, "MIGRATIONS", tmp_path)
    conn = connect()
    migrate_module.migrate(conn)
    first = sorted(tmp_path.glob("*.sql"))[0]
    first.write_text(first.read_text() + "\n-- edited\n")
    with pytest.raises(RuntimeError, match="has changed"):
        migrate_module.migrate(conn)


def test_transaction_rolls_back():
    conn = connect()
    migrate(conn)
    with pytest.raises(RuntimeError), transaction(conn):
        conn.execute("INSERT INTO staff (email, name) VALUES ('a@b.c', 'A')")
        raise RuntimeError("something went wrong")
    assert conn.execute("SELECT COUNT(*) FROM staff").fetchone()[0] == 0
