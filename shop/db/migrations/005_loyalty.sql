ALTER TABLE customers ADD COLUMN loyalty_balance INTEGER NOT NULL DEFAULT 0;

ALTER TABLE orders ADD COLUMN loyalty_points_earned INTEGER NOT NULL DEFAULT 0;
ALTER TABLE orders ADD COLUMN loyalty_points_redeemed INTEGER NOT NULL DEFAULT 0;

CREATE TABLE order_adjustments (
    order_id INTEGER NOT NULL REFERENCES orders (id),
    position INTEGER NOT NULL,
    kind TEXT NOT NULL,
    description TEXT NOT NULL,
    amount_pence INTEGER NOT NULL CHECK (amount_pence > 0),
    PRIMARY KEY (order_id, position)
);
