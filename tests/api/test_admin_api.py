import pytest

from tests.conftest import auth


@pytest.fixture
def staff_token(make):
    return make.staff()[1]


@pytest.mark.parametrize(
    "method, path",
    [
        ("post", "/admin/products"),
        ("put", "/admin/products/TEE/price"),
        ("get", "/admin/orders/1"),
        ("post", "/admin/orders/1/dispatch"),
        ("put", "/admin/customers/1/employee-discount"),
        ("get", "/admin/audit"),
    ],
)
def test_admin_needs_staff(client, make, method, path):
    _, customer_token = make.customer()
    assert getattr(client, method)(path).status_code == 401
    assert getattr(client, method)(path, headers=auth(customer_token)).status_code == 403


def test_create_product(client, staff_token):
    response = client.post(
        "/admin/products",
        json={"sku": "SCARF", "name": "Scarf", "category": "clothing", "price": "25.00"},
        headers=auth(staff_token),
    )
    assert response.status_code == 201
    assert client.get("/products/SCARF").json()["price"] == "25.00"


def test_create_product_bad_price(client, staff_token):
    response = client.post(
        "/admin/products",
        json={"sku": "SCARF", "name": "Scarf", "category": "clothing", "price": "25.001"},
        headers=auth(staff_token),
    )
    assert response.status_code == 422


def test_change_price_and_audit(client, make, staff_token):
    make.product("TEE", price="20.00")
    client.put("/admin/products/TEE/price", json={"price": "22.00"}, headers=auth(staff_token))
    [entry] = client.get("/admin/audit?subject=product:TEE", headers=auth(staff_token)).json()
    assert entry["action"] == "product.price_changed"
    assert entry["details"] == {"old": "20.00", "new": "22.00"}


def test_dispatch(client, make, staff_token):
    make.product("TEE", price="20.00")
    customer, token = make.customer()
    order = client.post(
        "/checkout",
        json={"cart_id": make.cart(customer, ("TEE", 1)), "payment_token": "tok_visa"},
        headers=auth(token),
    ).json()

    dispatched = client.post(f"/admin/orders/{order['id']}/dispatch", headers=auth(staff_token))
    assert dispatched.json()["status"] == "dispatched"
    again = client.post(f"/admin/orders/{order['id']}/dispatch", headers=auth(staff_token))
    assert again.status_code == 409


def test_set_employee_discount(client, make, staff_token):
    customer, token = make.customer()
    response = client.put(
        f"/admin/customers/{customer.id}/employee-discount",
        json={"percent": 20},
        headers=auth(staff_token),
    )
    assert response.json()["employee_discount_percent"] == 20
    me = client.get("/customers/me", headers=auth(token)).json()
    assert me["employee_discount_percent"] == 20


def test_employee_discount_limits(client, make, staff_token):
    customer, _ = make.customer()
    response = client.put(
        f"/admin/customers/{customer.id}/employee-discount",
        json={"percent": 51},
        headers=auth(staff_token),
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_failed"


def test_employee_discount_unknown_customer(client, staff_token):
    response = client.put(
        "/admin/customers/12345/employee-discount", json={"percent": 20}, headers=auth(staff_token)
    )
    assert response.status_code == 404
