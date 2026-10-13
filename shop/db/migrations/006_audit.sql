CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY,
    staff_id INTEGER NOT NULL REFERENCES staff (id),
    action TEXT NOT NULL,
    subject TEXT NOT NULL,
    details TEXT NOT NULL,
    created_at TEXT NOT NULL
);
