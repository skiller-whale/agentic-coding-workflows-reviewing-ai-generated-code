from tests.conftest import auth


def test_list_products(client, make):
    make.product("TEE", price="20.00", name="Tee")
    response = client.get("/products")
    assert response.status_code == 200
    assert response.json() == [
        {"sku": "TEE", "name": "Tee", "description": "", "category": "clothing", "price": "20.00"}
    ]


def test_filter_by_category(client, make):
    make.product("TEE", category="clothing")
    make.product("MUG", category="kitchen")
    assert [p["sku"] for p in client.get("/products?category=kitchen").json()] == ["MUG"]


def test_get_product(client, make):
    make.product("TEE", price="20.00")
    assert client.get("/products/TEE").json()["price"] == "20.00"


def test_unknown_product(client):
    response = client.get("/products/NOPE")
    assert response.status_code == 404
    assert response.json() == {"error": {"code": "not_found", "message": "No product 'NOPE'"}}


def test_register_and_me(client):
    response = client.post("/customers", json={"email": "alice@example.com", "name": "Alice"})
    assert response.status_code == 201
    token = response.json()["token"]
    me = client.get("/customers/me", headers=auth(token)).json()
    assert me["email"] == "alice@example.com"
    assert me["loyalty_balance"] == 0
    assert me["employee_discount_percent"] == 0


def test_me_needs_a_token(client):
    response = client.get("/customers/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_bad_token(client):
    assert client.get("/customers/me", headers=auth("nope")).status_code == 401


def test_staff_arent_customers(client, make):
    _, token = make.staff()
    assert client.get("/customers/me", headers=auth(token)).status_code == 403
