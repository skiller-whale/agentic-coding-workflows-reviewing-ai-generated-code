CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers (id),
    status TEXT NOT NULL,
    merchandise_pence INTEGER NOT NULL,
    tax_pence INTEGER NOT NULL,
    shipping_pence INTEGER NOT NULL,
    total_pence INTEGER NOT NULL,
    payment_ref TEXT NOT NULL,
    placed_at TEXT NOT NULL,
    dispatched_at TEXT
);

CREATE TABLE order_lines (
    order_id INTEGER NOT NULL REFERENCES orders (id),
    position INTEGER NOT NULL,
    sku TEXT NOT NULL,
    name TEXT NOT NULL,
    unit_price_pence INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (order_id, position)
);

CREATE INDEX orders_by_customer ON orders (customer_id, placed_at);
