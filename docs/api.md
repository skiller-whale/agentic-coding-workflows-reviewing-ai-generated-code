# Shop API

All amounts are strings of pounds with two decimal places, e.g. `"12.50"`.
Authenticate with `Authorization: Bearer <token>`. Errors look like
`{"error": {"code": "not_found", "message": "No order 12"}}`.

| Status | Code                                                              |
| ------ | ----------------------------------------------------------------- |
| 401    | `unauthorized`                                                    |
| 402    | `payment_declined`                                                |
| 403    | `forbidden`                                                       |
| 404    | `not_found`                                                       |
| 409    | `conflict`                                                        |
| 422    | `validation_failed` (and FastAPI's own request validation errors) |

## Public

| Method | Path                  | Notes                                       |
| ------ | --------------------- | ------------------------------------------- |
| `GET`  | `/products?category=` |                                             |
| `GET`  | `/products/{sku}`     |                                             |
| `POST` | `/customers`          | Register. Returns the customer and a token. |

## Customers

| Method | Path                      | Notes                                                               |
| ------ | ------------------------- | ------------------------------------------------------------------- |
| `GET`  | `/customers/me`           | Includes `loyalty_balance` and `employee_discount_percent`.         |
| `POST` | `/carts`                  | Create an empty cart.                                               |
| `GET`  | `/carts/{id}`             | Lines, and a price preview.                                         |
| `PUT`  | `/carts/{id}/lines/{sku}` | `{"quantity"}`; 0 removes the line.                                 |
| `POST` | `/checkout`               | `{"cart_id", "payment_token", "redeem_points"}`. Returns the order. |
| `GET`  | `/orders`                 | The customer's orders, newest first.                                |
| `GET`  | `/orders/{id}`            |                                                                     |
| `POST` | `/orders/{id}/cancel`     | Until dispatched; refunds in full.                                  |

## Staff

All under `/admin`, and all need a staff token. Every change is recorded in the
audit log.

| Method | Path                                      | Notes                                                 |
| ------ | ----------------------------------------- | ----------------------------------------------------- |
| `POST` | `/admin/products`                         | `{"sku", "name", "category", "price", "description"}` |
| `PUT`  | `/admin/products/{sku}/price`             | `{"price"}`                                           |
| `GET`  | `/admin/orders/{id}`                      |                                                       |
| `POST` | `/admin/orders/{id}/dispatch`             |                                                       |
| `PUT`  | `/admin/customers/{id}/employee-discount` | `{"percent"}`, from 0 to 50.                          |
| `GET`  | `/admin/audit?subject=&limit=`            | Newest first.                                         |

## Pricing

- `merchandise` is the sum of the lines.
- `adjustments` come off the merchandise before tax. Each has a `kind`:
  - `employee`: staff get their `employee_discount_percent` off the merchandise.
  - `loyalty`: redeemed loyalty points.
- Prices include VAT, so `tax` is the VAT included in the total.
- Shipping is £4.95, and free when the merchandise, before adjustments, is at
  least £50.
- Loyalty points are earned at 1 per whole pound paid for merchandise, and can
  pay for up to half the merchandise at 1p each.
