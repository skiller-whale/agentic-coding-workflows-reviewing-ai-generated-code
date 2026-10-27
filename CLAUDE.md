# shop

The API for a small online shop in the UK: customers check out a list of items, and staff add products.
Python, FastAPI and SQLite.

## Commands

- `uv run pytest` - run the tests.
- `uv run fastapi dev shop/app.py` - run the API locally.

## Layout

- `shop/money.py` - `Money`, an amount in pence.
- `shop/pricing.py` - pricing an order: subtotal, shipping and total.
- `shop/db.py` - the SQLite connection, migrations, and queries.
- `shop/schemas.py` - the shapes of requests and responses.
- `shop/app.py` - the routes.
- `migrations/` - the schema, as SQL files run in order.
- `tests/` - the tests.
- `docs/api.md` - the API documentation.
