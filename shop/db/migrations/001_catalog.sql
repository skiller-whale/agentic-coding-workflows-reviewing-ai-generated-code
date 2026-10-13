CREATE TABLE products (
    sku TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    category TEXT NOT NULL,
    price_pence INTEGER NOT NULL CHECK (price_pence >= 0)
);
