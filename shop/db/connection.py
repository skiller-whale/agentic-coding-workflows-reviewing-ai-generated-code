import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager


def connect(database: str = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(database, check_same_thread=False, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    """Run a block in a transaction, committing on success and rolling back on error.

    Nested calls join the outer transaction.
    """
    if conn.in_transaction:
        yield conn
        return
    conn.execute("BEGIN")
    try:
        yield conn
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    conn.execute("COMMIT")
