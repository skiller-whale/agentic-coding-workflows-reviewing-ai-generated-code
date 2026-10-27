import re

from shop.app import app


def test_list_products(client, add_product):
    add_product("TEE", "15.00", name="T-shirt")
    add_product("MUG", "8.00", name="Mug")

    response = client.get("/products")

    assert response.json() == [
        {"sku": "MUG", "name": "Mug", "price": "8.00"},
        {"sku": "TEE", "name": "T-shirt", "price": "15.00"},
    ]


def test_add_product_with_an_existing_sku(client, staff_headers, add_product):
    add_product("TEE", "15.00")

    response = client.post(
        "/admin/products",
        json={"sku": "TEE", "name": "Another T-shirt", "price": "12.00"},
        headers=staff_headers,
    )

    assert response.status_code == 409


def test_checkout(client, add_product):
    add_product("TEE", "15.00")
    add_product("MUG", "8.00")

    response = client.post(
        "/checkout",
        json={"items": [{"sku": "TEE", "quantity": 1}, {"sku": "MUG", "quantity": 2}]},
    )

    assert response.status_code == 201
    assert response.json() == {
        "order_id": 1,
        "subtotal": "31.00",
        "shipping": "4.95",
        "total": "35.95",
    }


def test_checkout_with_free_shipping(client, add_product):
    add_product("HOODIE", "55.00")

    response = client.post("/checkout", json={"items": [{"sku": "HOODIE", "quantity": 1}]})

    assert response.json()["shipping"] == "0.00"
    assert response.json()["total"] == "55.00"


def test_checkout_with_an_unknown_product(client):
    response = client.post("/checkout", json={"items": [{"sku": "NOPE", "quantity": 1}]})

    assert response.status_code == 422


def test_checkout_stores_the_order(client, staff_headers, add_product):
    add_product("TEE", "15.00")
    order_id = client.post(
        "/checkout", json={"items": [{"sku": "TEE", "quantity": 2}]}
    ).json()["order_id"]

    response = client.get(f"/admin/orders/{order_id}", headers=staff_headers)

    assert response.json() == {
        "id": order_id,
        "items": [{"sku": "TEE", "price": "15.00", "quantity": 2}],
        "subtotal": "30.00",
        "shipping": "4.95",
        "total": "34.95",
    }


def test_get_an_order_that_does_not_exist(client, staff_headers):
    response = client.get("/admin/orders/99", headers=staff_headers)

    assert response.status_code == 404


def test_admin_routes_need_staff(client):
    paths = app.openapi()["paths"]
    admin_routes = [
        (method, path) for path in paths if path.startswith("/admin") for method in paths[path]
    ]
    assert admin_routes

    for method, path in admin_routes:
        for headers in [{}, {"X-API-Key": "wrong"}]:
            response = client.request(method, re.sub(r"{\w+}", "1", path), headers=headers)
            assert response.status_code == 401, f"{method} {path}"
