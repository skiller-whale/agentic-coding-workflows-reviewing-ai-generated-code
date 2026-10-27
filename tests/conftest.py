import pytest
from fastapi.testclient import TestClient

from shop import db
from shop.app import STAFF_API_KEY, app
from shop.db import get_db


@pytest.fixture
def client():
    conn = db.connect(":memory:")
    app.dependency_overrides[get_db] = lambda: conn
    yield TestClient(app)
    app.dependency_overrides.clear()
    conn.close()


@pytest.fixture
def staff_headers():
    return {"X-API-Key": STAFF_API_KEY}


@pytest.fixture
def add_product(client, staff_headers):
    def add(sku, price, name="A product"):
        response = client.post(
            "/admin/products",
            json={"sku": sku, "name": name, "price": price},
            headers=staff_headers,
        )
        assert response.status_code == 201

    return add
