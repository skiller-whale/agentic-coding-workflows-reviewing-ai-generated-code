CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE staff (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL
);

CREATE TABLE api_tokens (
    token TEXT PRIMARY KEY,
    customer_id INTEGER REFERENCES customers (id),
    staff_id INTEGER REFERENCES staff (id),
    CHECK ((customer_id IS NULL) <> (staff_id IS NULL))
);
