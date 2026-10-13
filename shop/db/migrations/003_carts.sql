CREATE TABLE carts (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers (id)
);

CREATE TABLE cart_lines (
    cart_id INTEGER NOT NULL REFERENCES carts (id) ON DELETE CASCADE,
    sku TEXT NOT NULL REFERENCES products (sku),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (cart_id, sku)
);
