# shop

The API behind a small online shop in the UK.

## Commands

- `uv run pytest` - run the tests.
- `uv run ruff check .` and `uv run ruff format .` - lint and format.

## Layout

- `shop/api/` - the FastAPI app, routes and request/response schemas.
- `shop/services/` - application services.
- `shop/domain/` - the domain model and pricing rules.
- `shop/repositories/` - database access.
- `shop/db/` - the SQLite connection and migrations.
- `docs/` - API documentation.
