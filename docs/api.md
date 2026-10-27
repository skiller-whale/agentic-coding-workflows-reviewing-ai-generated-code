# Shop API

All amounts are in pounds, as strings with two decimal places (e.g. `"12.50"`).

## Routes

| Route                        | Who   | What                                                                  |
| ---------------------------- | ----- | --------------------------------------------------------------------- |
| `GET /products`              | All   | List the products.                                                    |
| `POST /checkout`             | All   | Place an order: `{"items": [{"sku": "TEE", "quantity": 2}]}`.         |
| `POST /admin/products`       | Staff | Add a product: `{"sku": "TEE", "name": "T-shirt", "price": "15.00"}`. |
| `GET /admin/orders/{id}`     | Staff | Get an order.                                                         |

Staff routes need the staff API key in an `X-API-Key` header.

## Pricing

- The **subtotal** is the sum of each item's price times its quantity.
- **Shipping** is £4.95, and free when the subtotal is £50 or more.
- The **total** is the subtotal plus shipping.

`POST /checkout` returns the order's ID and its price:

```json
{"order_id": 1, "subtotal": "31.00", "shipping": "4.95", "total": "35.95"}
```
