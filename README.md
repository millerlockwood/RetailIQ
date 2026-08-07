# RetailIQ

## Retail Demand Forecasting & Inventory Optimization Platform

RetailIQ is an end-to-end retail analytics platform built to transform raw retail sales data into validated, analytics-ready information for reporting, forecasting, inventory analysis, and business decision support.

The project demonstrates data engineering, SQL warehouse design, business analytics, and business intelligence development using the M5 retail dataset.

---

## Architecture

```text
Raw M5 Retail Data
        |
        v
Data Profiling
        |
        v
Data Validation
        |
        v
Data Cleaning
        |
        v
Wide-to-Long Transformation
        |
        v
SQLite Data Warehouse
        |
        v
SQL Views & Summary Tables
        |
        v
Python Analytics
        |
        v
Dashboard Data Exports
        |
        v
Power BI
        |
        v
Forecasting & Inventory Optimization
```

---

## Current Capabilities

RetailIQ currently includes:

- Automated data profiling
- Rule-based data validation
- Cross-table relationship validation
- Automated Markdown reporting
- Memory-optimized data cleaning
- Wide-to-long transformation of retail sales data
- SQL star-schema-style data warehouse
- Automated database creation and loading
- More than 66 million warehouse records
- SQL indexes for query performance
- Reusable analytical views
- Precomputed summary tables for faster reporting
- Python-based business analytics
- Automated dashboard data exports
- Executive Power BI dashboard
- Store and product performance analysis

---

## Technology Stack

- Python
- Pandas
- NumPy
- PyArrow
- SQLite
- SQL
- Power BI
- Streamlit
- Git
- GitHub
- VS Code

---

## Data Warehouse

RetailIQ uses a star-schema-style warehouse with three dimensions and two core fact tables.

### Dimension Tables

- `dim_calendar`
- `dim_product`
- `dim_store`

### Fact Tables

- `fact_daily_sales`
- `fact_sell_prices`

### Reporting Layer

- `summary_store_sales`
- `summary_state_sales`
- `summary_product_sales`
- `summary_category_sales`
- `summary_monthly_sales`

The warehouse contains more than **66 million sales records**.

Summary tables reduce the amount of data that downstream analytics and business intelligence tools need to process.

---

## ETL Pipeline

The ETL workflow is organized into reusable stages:

```text
01_data_overview.py
02_data_validation.py
03_data_cleaning.py
04_transform_sales.py
05_build_database.py
06_load_database.py
07_create_indexes.py
08_create_views.py
09_create_summary_tables.py
```

Each stage performs a specific responsibility, allowing the project to move from raw source data to an analytics-ready SQL warehouse.

Several stages also automatically generate documentation in the `reports/` directory.

---

## Analytics Layer

RetailIQ includes a Python analytics layer that queries the SQL warehouse and prepares business-focused datasets for reporting.

The analytics workflow produces dashboard-ready outputs including:

- Monthly unit sales
- Top-selling products
- Store performance
- State performance
- Category sales
- Executive KPIs
- Average daily store sales

Dashboard datasets are exported to:

```text
reports/dashboard_data/
```

This separates the large analytical warehouse from the lightweight datasets consumed by Power BI.

---

## Power BI Dashboard

RetailIQ includes a two-page Power BI report designed for executive reporting and detailed performance analysis.

### Page 1 — Executive Dashboard

The executive dashboard provides a high-level view of retail performance, including:

- **66,927,173 total units sold**
- **3,049 products**
- **10 stores**
- Top-performing store
- Top-performing state
- Top-performing category
- Monthly sales trends
- Top 10 products
- Top 10 stores
- Sales by state
- Sales by category

### Page 2 — Store & Product Performance

The detailed performance page includes:

- Average daily sales by store
- Top 10 products by units sold
- Store sales performance comparison
- Category sales mix

The store performance analysis compares total sales volume with average daily sales to identify differences in performance across locations.

---

## Key Business Insights

Initial analysis identified several clear performance patterns:

- **FOODS** is the dominant product category and represents the majority of unit sales.
- **California** is the highest-volume state.
- **CA_3** is the highest-performing store by total units sold.
- Store performance varies substantially across the 10 locations.
- A relatively small group of products accounts for the highest individual product sales.
- Monthly demand fluctuates throughout the year rather than remaining constant.

These findings establish the descriptive analytics foundation for the project's future forecasting and inventory optimization stages.

---

## Automated Reports

RetailIQ generates:

- `01_Data_Quality_Report.md`
- `02_Validation_Report.md`
- `03_Cleaning_Report.md`
- `04_Transformation_Report.md`

These reports document data quality, validation results, cleaning actions, memory optimization, and transformation outcomes.

---

## Project Structure

```text
RetailIQ/
|
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
|
├── database/
├── docs/
├── reports/
│   └── dashboard_data/
|
├── sql/
|
├── src/
│   ├── analytics/
│   └── etl/
|
├── dashboard/
├── notebooks/
├── tests/
|
├── README.md
├── requirements.txt
└── .gitignore
```

Large raw datasets, processed datasets, and generated database files are excluded from GitHub and can be recreated using the project pipeline.

---

## SQL Layer

The SQL layer includes:

- Warehouse table creation
- Index creation
- Analytical views
- Business queries
- Precomputed summary tables

The analytical layer supports questions such as:

- Which stores generate the highest unit sales?
- Which products and categories drive the most demand?
- How does demand differ by state?
- How does demand change over time?
- Which stores have the strongest average daily performance?
- How do holidays and SNAP participation affect sales?
- How do selling prices relate to product demand?

---

## Current Development Status

- [x] Project foundation
- [x] Business requirements
- [x] Data acquisition
- [x] Data profiling
- [x] Data validation
- [x] Data cleaning
- [x] Sales transformation
- [x] SQL warehouse design
- [x] Automated database loading
- [x] SQL indexes
- [x] SQL views
- [x] Summary reporting tables
- [x] Exploratory business analysis
- [x] Dashboard data export pipeline
- [x] Power BI executive dashboard
- [x] Store and product performance dashboard
- [ ] Pipeline automation
- [ ] Feature engineering
- [ ] Demand forecasting
- [ ] Inventory optimization
- [ ] Streamlit application
- [ ] Executive report
- [ ] Version 1.0 release

---

## Documentation

Project documentation is available in the `docs/` directory.

Current documents include:

- Business Requirements
- Project Roadmap
- SQL Warehouse Architecture

---

## Dataset

RetailIQ uses the **M5 Forecasting dataset**, which contains historical retail sales, pricing, calendar, event, and store information.

The raw dataset is not stored in this repository due to file size.

Users must obtain the dataset separately and place the required source files in:

```text
data/raw/
```

---

## Project Goal

RetailIQ is being developed to move from descriptive retail analytics toward predictive and prescriptive decision support.

The final platform will answer:

> **How much inventory should each store order to reduce stockouts while minimizing excess inventory cost?**

Future development will combine demand forecasting, inventory optimization, and executive reporting to translate historical retail data into actionable inventory decisions.

---

## Author

**Miller Lockwood**