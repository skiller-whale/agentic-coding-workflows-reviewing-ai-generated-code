# shop

The API behind a small online shop in the UK.

```
uv sync                                                   # install the dependencies into .venv
uv run pytest                                             # run the tests
uv run python -m shop.seed shop.db                        # create a database with demo data
SHOP_DATABASE=shop.db uv run fastapi dev shop/api/app.py  # start the API on http://127.0.0.1:8000
```

The API is documented in `docs/api.md`.
