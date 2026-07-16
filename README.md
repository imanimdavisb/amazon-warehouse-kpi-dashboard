# Amazon Warehouse KPI Dashboard

![Dashboard](dashboard.png)

## Overview

This project is an interactive warehouse operations dashboard built with **Python, SQL, SQLite, Streamlit, and Plotly**. It uses simulated Amazon-style warehouse performance data to help Operations Managers monitor productivity, quality, safety, and operational performance through interactive KPIs, charts, filters, and data-driven recommendations.

> **Disclaimer:** This is a portfolio project built using simulated warehouse data. It is not affiliated with or endorsed by Amazon.

---

# Executive Summary

The dashboard provides key operational metrics including:

* Orders Picked Today
* Order Accuracy
* Units Per Hour (UPH)
* Safety Incidents
* Quality Score

Managers can filter results by **Month**, **Shift**, and **Department** to quickly identify operational trends and performance opportunities.

---

# Dashboard Features

## Executive KPIs

* Orders Picked Today
* Order Accuracy
* Units Per Hour
* Safety Incidents
* Quality Score

## Interactive Charts

* Pick Rate by Week
* Accuracy by Department
* Quality Defects by Department
* Safety Incidents by Month
* Productivity by Shift

## Interactive Filters

* Month
* Shift
* Department

## Dynamic Operations Manager Insights

The dashboard automatically analyzes the filtered data and generates operational recommendations, including:

* Comparing Day Shift and Night Shift productivity
* Identifying departments with the highest quality defects
* Highlighting departments with the lowest order accuracy
* Flagging safety incidents requiring supervisor review
* Recommending cross-training opportunities when productivity gaps exist

---

# Technologies Used

* Python
* SQL
* SQLite
* Streamlit
* Plotly
* Pandas

---

# Project Structure

```text
amazon_warehouse_kpi_dashboard/

├── app.py
├── generate_data.py
├── setup_database.py
├── requirements.txt
├── README.md
├── warehouse_kpis.db
├── data/
│   └── warehouse_performance.csv
└── sql/
    ├── schema.sql
    └── kpi_queries.sql
```

---

# Skills Demonstrated

* SQL Query Development
* Business Analytics
* KPI Reporting
* Dashboard Development
* Data Visualization
* Business Intelligence
* Operations Analytics
* Process Improvement
* Data Storytelling

---

# Sample Business Questions Answered

* Which shift has the highest productivity?
* Which department has the lowest order accuracy?
* Where are the most quality defects occurring?
* Are safety incidents increasing over time?
* Which operational area requires immediate management attention?

---

# Future Improvements

* Employee performance dashboard
* Labor cost and overtime analysis
* KPI target vs. actual scorecards
* Pareto chart for quality defects
* Forecast next week's order volume
* PDF and Excel report exports
* Live database integration
* Power BI version of the dashboard

---

# Key Takeaways

This project demonstrates how SQL and Python can be used together to transform operational data into actionable business insights. It showcases dashboard development, KPI reporting, and decision-support techniques commonly used in warehouse, supply chain, and operations management environments.

---

# Author

**Imani Davis**

GitHub: https://github.com/imanimdavisb

LinkedIn: *(Add your LinkedIn profile URL here.)*
