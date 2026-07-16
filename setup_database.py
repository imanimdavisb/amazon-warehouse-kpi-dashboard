from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).parent
DB_PATH = ROOT / "warehouse_kpis.db"
CSV_PATH = ROOT / "data" / "warehouse_performance.csv"
SCHEMA_PATH = ROOT / "sql" / "schema.sql"

INSERT_SQL = """
INSERT INTO warehouse_performance (
    record_id,
    work_date,
    month,
    week_start,
    shift,
    department,
    employee_count,
    labor_hours,
    units_picked,
    orders_picked,
    accurate_orders,
    quality_defects,
    safety_incidents
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

def main() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            "Sample data was not found. Run: python generate_data.py"
        )

    connection = sqlite3.connect(DB_PATH)

    try:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

        with CSV_PATH.open("r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            rows = [
                (
                    int(row["record_id"]),
                    row["work_date"],
                    row["month"],
                    row["week_start"],
                    row["shift"],
                    row["department"],
                    int(row["employee_count"]),
                    float(row["labor_hours"]),
                    int(row["units_picked"]),
                    int(row["orders_picked"]),
                    int(row["accurate_orders"]),
                    int(row["quality_defects"]),
                    int(row["safety_incidents"]),
                )
                for row in reader
            ]

        connection.executemany(INSERT_SQL, rows)
        connection.commit()

        count = connection.execute(
            "SELECT COUNT(*) FROM warehouse_performance"
        ).fetchone()[0]

        print(f"Loaded {count:,} records into {DB_PATH}")
    finally:
        connection.close()

if __name__ == "__main__":
    main()
