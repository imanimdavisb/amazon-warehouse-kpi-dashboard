from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

OUTPUT = Path(__file__).parent / "data" / "warehouse_performance.csv"
random.seed(42)

DEPARTMENTS = {
    "Pick": {"uph": 305, "accuracy": 0.991, "defect_rate": 0.0025},
    "Pack": {"uph": 245, "accuracy": 0.994, "defect_rate": 0.0018},
    "Stow": {"uph": 220, "accuracy": 0.987, "defect_rate": 0.0032},
    "Receive": {"uph": 190, "accuracy": 0.989, "defect_rate": 0.0028},
    "Sort": {"uph": 270, "accuracy": 0.992, "defect_rate": 0.0022},
}

SHIFTS = {
    "Day": 1.04,
    "Night": 0.97,
    "Weekend": 0.92,
}

def monday_of(day: date) -> date:
    return day - timedelta(days=day.weekday())

def build_rows() -> list[dict]:
    rows: list[dict] = []
    current = date(2026, 1, 1)
    end = date(2026, 6, 30)
    record_id = 1

    while current <= end:
        seasonal = 1 + (current.month - 1) * 0.012

        for department, profile in DEPARTMENTS.items():
            for shift, shift_factor in SHIFTS.items():
                employees = random.randint(18, 42)
                hours_per_employee = random.uniform(8.4, 10.2)
                labor_hours = employees * hours_per_employee

                noise = random.uniform(0.91, 1.09)
                units = round(
                    profile["uph"] * shift_factor * seasonal *
                    labor_hours * noise
                )

                average_units_per_order = random.uniform(2.2, 3.8)
                orders = max(1, round(units / average_units_per_order))

                accuracy_rate = min(
                    0.999,
                    max(
                        0.965,
                        profile["accuracy"]
                        + random.uniform(-0.0045, 0.0035)
                    )
                )
                accurate_orders = round(orders * accuracy_rate)

                defect_rate = max(
                    0.0005,
                    profile["defect_rate"] *
                    random.uniform(0.70, 1.35)
                )
                defects = max(0, round(units * defect_rate))

                incident_probability = (
                    0.012
                    + (0.007 if shift == "Night" else 0)
                    + (0.004 if department in {"Receive", "Stow"} else 0)
                )
                incidents = 1 if random.random() < incident_probability else 0

                rows.append({
                    "record_id": record_id,
                    "work_date": current.isoformat(),
                    "month": current.strftime("%Y-%m"),
                    "week_start": monday_of(current).isoformat(),
                    "shift": shift,
                    "department": department,
                    "employee_count": employees,
                    "labor_hours": round(labor_hours, 2),
                    "units_picked": units,
                    "orders_picked": orders,
                    "accurate_orders": accurate_orders,
                    "quality_defects": defects,
                    "safety_incidents": incidents,
                })
                record_id += 1

        current += timedelta(days=1)

    return rows

def main() -> None:
    OUTPUT.parent.mkdir(exist_ok=True)
    rows = build_rows()

    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created {len(rows):,} rows at {OUTPUT}")

if __name__ == "__main__":
    main()
