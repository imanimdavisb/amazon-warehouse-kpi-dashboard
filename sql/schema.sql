DROP TABLE IF EXISTS warehouse_performance;

CREATE TABLE warehouse_performance (
    record_id INTEGER PRIMARY KEY,
    work_date TEXT NOT NULL,
    month TEXT NOT NULL,
    week_start TEXT NOT NULL,
    shift TEXT NOT NULL,
    department TEXT NOT NULL,
    employee_count INTEGER NOT NULL,
    labor_hours REAL NOT NULL,
    units_picked INTEGER NOT NULL,
    orders_picked INTEGER NOT NULL,
    accurate_orders INTEGER NOT NULL,
    quality_defects INTEGER NOT NULL,
    safety_incidents INTEGER NOT NULL
);
