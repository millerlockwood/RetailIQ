# RetailIQ SQL Warehouse Architecture

## Purpose

The RetailIQ SQL Warehouse is designed to support business intelligence, forecasting, and inventory optimization.

Instead of querying large CSV files directly, the warehouse stores cleaned and transformed data in an analytics-friendly relational database.

This architecture improves:

- Query performance
- Data organization
- Scalability
- Power BI integration
- Machine learning workflows

---

# Warehouse Design

RetailIQ uses a star schema consisting of fact tables and dimension tables.

```
                dim_calendar
                     |
                     |
dim_product --> fact_daily_sales <-- dim_store
      |
      |
      +-------- fact_sell_prices
```

---

# Dimension Tables

## dim_calendar

Purpose:

Stores one record for every calendar date.

Primary Key:

```
date
```

Contains:

- Date
- Retail Week
- Month
- Year
- Weekday
- SNAP indicators
- Holiday information

---

## dim_product

Purpose:

Stores product information.

Primary Key:

```
item_id
```

Contains:

- Item ID
- Department
- Category

---

## dim_store

Purpose:

Stores store information.

Primary Key:

```
store_id
```

Contains:

- Store ID
- State

---

# Fact Tables

## fact_daily_sales

Purpose:

Stores one record for every product sold in every store on every date.

Primary Key:

```
date
store_id
item_id
```

Contains:

- Date
- Store
- Product
- Sales
- Retail Week

---

## fact_sell_prices

Purpose:

Stores weekly selling prices for each product.

Primary Key:

```
wm_yr_wk
store_id
item_id
```

Contains:

- Retail Week
- Store
- Product
- Selling Price

---

# Data Flow

```
Raw CSV Files
      │
      ▼
01 Data Overview
      │
      ▼
02 Validation
      │
      ▼
03 Cleaning
      │
      ▼
04 Sales Transformation
      │
      ▼
SQLite Warehouse
      │
      ▼
Power BI
      │
      ▼
Forecasting
      │
      ▼
Inventory Optimization
```

---

# Why a Star Schema?

The star schema was selected because it:

- Simplifies SQL queries
- Improves Power BI performance
- Separates descriptive data from transactional data
- Supports future expansion
- Matches common data warehouse design practices

---

# Future Enhancements

Future versions of RetailIQ will include:

- Forecast tables
- Inventory recommendation tables
- Executive KPI views
- Materialized summary tables