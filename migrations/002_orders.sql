CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    subtotal_pence INTEGER NOT NULL,
    shipping_pence INTEGER NOT NULL,
    total_pence INTEGER NOT NULL
);

CREATE TABLE order_lines (
    order_id INTEGER NOT NULL REFERENCES orders (id),
    sku TEXT NOT NULL REFERENCES products (sku),
    price_pence INTEGER NOT NULL,
    quantity INTEGER NOT NULL
);
