from tests.conftest import auth


def test_cart_to_order(client, make):
    make.product("TEE", price="20.00")
    customer, token = make.customer()

    cart = client.post("/carts", headers=auth(token)).json()
    cart = client.put(
        f"/carts/{cart['id']}/lines/TEE", json={"quantity": 2}, headers=auth(token)
    ).json()
    assert cart["preview"]["total"] == "44.95"

    response = client.post(
        "/checkout", json={"cart_id": cart["id"], "payment_token": "tok_visa"}, headers=auth(token)
    )
    assert response.status_code == 201
    order = response.json()
    assert order["total"] == "44.95"
    assert order["status"] == "placed"
    assert client.get("/orders", headers=auth(token)).json()[0]["id"] == order["id"]


def test_redeem_points(client, make):
    make.product("HOODIE", price="55.00")
    customer, token = make.customer(loyalty=1000)
    cart_id = make.cart(customer, ("HOODIE", 1))
    order = client.post(
        "/checkout",
        json={"cart_id": cart_id, "payment_token": "tok_visa", "redeem_points": 1000},
        headers=auth(token),
    ).json()
    assert order["adjustments"] == [
        {"kind": "loyalty", "description": "1000 loyalty points", "amount": "10.00"}
    ]
    assert order["total"] == "45.00"


def test_employee_discount(client, make):
    make.product("TEE", price="20.00")
    customer, token = make.customer(employee_discount=20)
    order = client.post(
        "/checkout",
        json={"cart_id": make.cart(customer, ("TEE", 1)), "payment_token": "tok_visa"},
        headers=auth(token),
    ).json()
    assert order["adjustments"] == [
        {"kind": "employee", "description": "20% employee discount", "amount": "4.00"}
    ]
    assert order["total"] == "20.95"


def test_declined(client, make):
    make.product("TEE")
    customer, token = make.customer()
    response = client.post(
        "/checkout",
        json={"cart_id": make.cart(customer, ("TEE", 1)), "payment_token": "tok_decline"},
        headers=auth(token),
    )
    assert response.status_code == 402
    assert response.json()["error"]["code"] == "payment_declined"


def test_too_many_points(client, make):
    make.product("TEE")
    customer, token = make.customer(loyalty=10)
    response = client.post(
        "/checkout",
        json={
            "cart_id": make.cart(customer, ("TEE", 1)),
            "payment_token": "tok_visa",
            "redeem_points": 11,
        },
        headers=auth(token),
    )
    assert response.status_code == 422


def test_cancel(client, make):
    make.product("TEE")
    customer, token = make.customer()
    order = client.post(
        "/checkout",
        json={"cart_id": make.cart(customer, ("TEE", 1)), "payment_token": "tok_visa"},
        headers=auth(token),
    ).json()
    response = client.post(f"/orders/{order['id']}/cancel", headers=auth(token))
    assert response.json()["status"] == "cancelled"
    assert client.post(f"/orders/{order['id']}/cancel", headers=auth(token)).status_code == 409


def test_other_customers_orders_are_hidden(client, make):
    make.product("TEE")
    alice, alice_token = make.customer()
    _, bob_token = make.customer()
    order = client.post(
        "/checkout",
        json={"cart_id": make.cart(alice, ("TEE", 1)), "payment_token": "tok_visa"},
        headers=auth(alice_token),
    ).json()
    assert client.get(f"/orders/{order['id']}", headers=auth(bob_token)).status_code == 404
