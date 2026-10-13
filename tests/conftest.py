from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from shop import clock
from shop.api.app import create_app
from shop.config import Settings
from shop.db.connection import connect
from shop.db.migrate import migrate
from shop.payments.gateway import FakeGateway
from shop.services import Services
from tests import factories

FROZEN_NOW = datetime(2026, 6, 15, 10, 0, tzinfo=UTC)


@pytest.fixture(autouse=True)
def frozen_clock(monkeypatch):
    monkeypatch.setattr(clock, "now", lambda: FROZEN_NOW)
    return FROZEN_NOW


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def conn():
    conn = connect(":memory:")
    migrate(conn)
    yield conn
    conn.close()


@pytest.fixture
def gateway():
    return FakeGateway()


@pytest.fixture
def services(conn, settings, gateway):
    return Services.build(conn, settings, gateway)


@pytest.fixture
def make(conn):
    return factories.Factories(conn)


@pytest.fixture
def client(conn, settings, gateway):
    return TestClient(create_app(settings=settings, conn=conn, gateway=gateway))


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
