import sqlite3
import subprocess
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).parent
DB_PATH = ROOT / "warehouse_kpis.db"

st.set_page_config(
    page_title="Amazon Warehouse KPI Dashboard",
    page_icon="📦",
    layout="wide",
)


@st.cache_resource
def get_connection():
    # first time the app runs there won't be a database yet, so build one
    if not DB_PATH.exists():
        subprocess.run([sys.executable, str(ROOT / "generate_data.py")], check=True)
        subprocess.run([sys.executable, str(ROOT / "setup_database.py")], check=True)

    return sqlite3.connect(DB_PATH, check_same_thread=False)


def query(sql, params=None):
    if params is None:
        params = []
    return pd.read_sql_query(sql, get_connection(), params=params)


def build_filter_clause(months, shifts, departments):
    # builds something like:
    # WHERE month IN (?,?) AND shift IN (?) AND department IN (?,?)
    conditions = []
    params = []

    if months:
        placeholders = ",".join("?" for _ in months)
        conditions.append("month IN (" + placeholders + ")")
        params.extend(months)

    if shifts:
        placeholders = ",".join("?" for _ in shifts)
        conditions.append("shift IN (" + placeholders + ")")
        params.extend(shifts)

    if departments:
        placeholders = ",".join("?" for _ in departments)
        conditions.append("department IN (" + placeholders + ")")
        params.extend(departments)

    if len(conditions) == 0:
        return "", params

    clause = " WHERE " + " AND ".join(conditions)
    return clause, params


connection = get_connection()

filter_options = query("""
SELECT DISTINCT month, shift, department
FROM warehouse_performance
ORDER BY month, shift, department
""")

all_months = sorted(filter_options["month"].dropna().unique().tolist())
all_shifts = sorted(filter_options["shift"].dropna().unique().tolist())
all_departments = sorted(filter_options["department"].dropna().unique().tolist())

st.title("Amazon Warehouse KPI Dashboard")
st.caption(
    "Portfolio project: SQL-powered operations dashboard using simulated "
    "warehouse data. This project is not affiliated with Amazon."
)

with st.sidebar:
    st.header("Dashboard Filters")
    selected_months = st.multiselect("Month", options=all_months, default=all_months)
    selected_shifts = st.multiselect("Shift", options=all_shifts, default=all_shifts)
    selected_departments = st.multiselect("Department", options=all_departments, default=all_departments)
    st.markdown("---")
    st.caption("Use filters to simulate an Operations Manager review.")

where_clause, params = build_filter_clause(selected_months, selected_shifts, selected_departments)

if not selected_months or not selected_shifts or not selected_departments:
    st.warning("Select at least one month, shift, and department.")
    st.stop()

latest_date_df = query(
    f"SELECT MAX(work_date) AS latest_date FROM warehouse_performance{where_clause}",
    params,
)
latest_date = latest_date_df.iloc[0]["latest_date"]

kpi_sql = f"""
SELECT
    SUM(CASE WHEN work_date = ? THEN orders_picked ELSE 0 END) AS orders_picked_today,
    ROUND(100.0 * SUM(accurate_orders) / NULLIF(SUM(orders_picked), 0), 2) AS order_accuracy,
    ROUND(1.0 * SUM(units_picked) / NULLIF(SUM(labor_hours), 0), 2) AS units_per_hour,
    SUM(safety_incidents) AS safety_incidents,
    ROUND(100.0 * (1 - 1.0 * SUM(quality_defects) / NULLIF(SUM(units_picked), 0)), 2) AS quality_score
FROM warehouse_performance
{where_clause}
"""

kpis = query(kpi_sql, [latest_date] + params).iloc[0]

st.subheader("Executive Summary")
st.caption(f"Orders Picked Today uses the latest filtered date: {latest_date}")

metric_columns = st.columns(5)
metric_columns[0].metric("Orders Picked Today", f"{int(kpis['orders_picked_today']):,}")
metric_columns[1].metric("Order Accuracy", f"{kpis['order_accuracy']:.2f}%")
metric_columns[2].metric("Units Per Hour", f"{kpis['units_per_hour']:.1f}")
metric_columns[3].metric("Safety Incidents", f"{int(kpis['safety_incidents']):,}")
metric_columns[4].metric("Quality Score", f"{kpis['quality_score']:.2f}%")

weekly_pick_rate = query(
    f"""
    SELECT
        week_start,
        ROUND(1.0 * SUM(units_picked) / NULLIF(SUM(labor_hours), 0), 2) AS pick_rate
    FROM warehouse_performance
    {where_clause}
    GROUP BY week_start
    ORDER BY week_start
    """,
    params,
)
weekly_pick_rate["week_start"] = pd.to_datetime(weekly_pick_rate["week_start"])

st.subheader("Trend Graph")
trend_chart = px.line(
    weekly_pick_rate,
    x="week_start",
    y="pick_rate",
    markers=True,
    title="Pick Rate by Week",
    labels={"week_start": "Week", "pick_rate": "Units per Hour"},
)
st.plotly_chart(trend_chart, use_container_width=True)

left, right = st.columns(2)

accuracy_department = query(
    f"""
    SELECT
        department,
        ROUND(100.0 * SUM(accurate_orders) / NULLIF(SUM(orders_picked), 0), 2) AS accuracy_pct
    FROM warehouse_performance
    {where_clause}
    GROUP BY department
    ORDER BY accuracy_pct DESC
    """,
    params,
)

with left:
    chart = px.bar(
        accuracy_department,
        x="department",
        y="accuracy_pct",
        text_auto=".2f",
        title="Accuracy by Department",
        labels={"department": "Department", "accuracy_pct": "Accuracy (%)"},
    )
    chart.update_yaxes(range=[max(0, accuracy_department["accuracy_pct"].min() - 1), 100])
    st.plotly_chart(chart, use_container_width=True)

quality_defects = query(
    f"""
    SELECT department, SUM(quality_defects) AS quality_defects
    FROM warehouse_performance
    {where_clause}
    GROUP BY department
    ORDER BY quality_defects DESC
    """,
    params,
)

with right:
    chart = px.bar(
        quality_defects,
        x="department",
        y="quality_defects",
        text_auto=True,
        title="Quality Defects",
        labels={"department": "Department", "quality_defects": "Defects"},
    )
    st.plotly_chart(chart, use_container_width=True)

left, right = st.columns(2)

safety = query(
    f"""
    SELECT month, SUM(safety_incidents) AS safety_incidents
    FROM warehouse_performance
    {where_clause}
    GROUP BY month
    ORDER BY month
    """,
    params,
)

with left:
    chart = px.bar(
        safety,
        x="month",
        y="safety_incidents",
        text_auto=True,
        title="Safety Incidents",
        labels={"month": "Month", "safety_incidents": "Incidents"},
    )
    st.plotly_chart(chart, use_container_width=True)

productivity = query(
    f"""
    SELECT
        shift,
        ROUND(1.0 * SUM(units_picked) / NULLIF(SUM(labor_hours), 0), 2) AS units_per_hour
    FROM warehouse_performance
    {where_clause}
    GROUP BY shift
    ORDER BY units_per_hour DESC
    """,
    params,
)

with right:
    chart = px.bar(
        productivity,
        x="shift",
        y="units_per_hour",
        text_auto=".1f",
        title="Productivity by Shift",
        labels={"shift": "Shift", "units_per_hour": "Units per Hour"},
    )
    st.plotly_chart(chart, use_container_width=True)

st.subheader("Department Scorecard")

scorecard = query(
    f"""
    SELECT
        department AS Department,
        SUM(orders_picked) AS Orders,
        SUM(units_picked) AS Units,
        ROUND(100.0 * SUM(accurate_orders) / NULLIF(SUM(orders_picked), 0), 2) AS "Accuracy %",
        ROUND(1.0 * SUM(units_picked) / NULLIF(SUM(labor_hours), 0), 2) AS UPH,
        SUM(quality_defects) AS Defects,
        SUM(safety_incidents) AS "Safety Incidents"
    FROM warehouse_performance
    {where_clause}
    GROUP BY department
    ORDER BY Units DESC
    """,
    params,
)

st.dataframe(scorecard, use_container_width=True, hide_index=True)

with st.expander("View SQL used for the weekly pick-rate chart"):
    st.code(
        """
SELECT
    week_start,
    ROUND(1.0 * SUM(units_picked) / NULLIF(SUM(labor_hours), 0), 2) AS pick_rate
FROM warehouse_performance
WHERE month IN (...)
  AND shift IN (...)
  AND department IN (...)
GROUP BY week_start
ORDER BY week_start;
        """.strip(),
        language="sql",
    )

# ---------------------------------------------------------------------------
# Operations Manager Insights
# these are generated from the same query results calculated above, not
# hardcoded, so the messages actually reflect whatever filters are selected
# ---------------------------------------------------------------------------
st.subheader("Operations Manager Insights")

insights = []

# compare units per hour between Day and Night shift, if both are in the filtered data
productivity_lookup = dict(zip(productivity["shift"], productivity["units_per_hour"]))
if "Day" in productivity_lookup and "Night" in productivity_lookup:
    day_rate = productivity_lookup["Day"]
    night_rate = productivity_lookup["Night"]
    gap_pct = round((day_rate - night_rate) / day_rate * 100, 1)
    if night_rate < day_rate:
        insights.append(f"🟡 Night Shift is running {gap_pct}% slower than Day Shift ({night_rate} vs {day_rate} units/hr).")
    else:
        insights.append(f"🟢 Night Shift is keeping pace with Day Shift ({night_rate} vs {day_rate} units/hr).")

# flag the department with the most quality defects
if len(quality_defects) > 0:
    top_defect_row = quality_defects.iloc[0]
    if top_defect_row["quality_defects"] > 0:
        insights.append(f"🟠 {top_defect_row['department']} has the highest defect count in this selection ({int(top_defect_row['quality_defects'])} defects). Worth a closer look.")

# flag the department with the lowest accuracy
if len(accuracy_department) > 0:
    lowest_accuracy_row = accuracy_department.sort_values("accuracy_pct").iloc[0]
    if lowest_accuracy_row["accuracy_pct"] < 99.0:
        insights.append(f"🟡 {lowest_accuracy_row['department']} has the lowest order accuracy in this selection ({lowest_accuracy_row['accuracy_pct']}%).")

# safety incidents always deserve a callout
if int(kpis["safety_incidents"]) > 0:
    insights.append(f"🔴 {int(kpis['safety_incidents'])} safety incident(s) were reported for this selection. Any incident should trigger a supervisor review.")
else:
    insights.append("🟢 No safety incidents reported for this selection.")

# general recommendation, tied to whether there is a meaningful shift gap
if "Day" in productivity_lookup and "Night" in productivity_lookup and productivity_lookup["Night"] < productivity_lookup["Day"] * 0.95:
    insights.append("💡 Recommendation: Cross-train associates to help close the gap between Day and Night shift throughput.")

for item in insights:
    st.info(item)
