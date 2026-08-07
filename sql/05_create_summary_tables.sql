-- ==========================================================
-- RetailIQ Summary Tables
-- ==========================================================

-------------------------------------------------------------
-- Store Sales Summary
-------------------------------------------------------------

DROP TABLE IF EXISTS summary_store_sales;

CREATE TABLE summary_store_sales AS

SELECT

    store_id,

    SUM(sales) AS total_units_sold,

    AVG(sales) AS average_daily_sales

FROM fact_daily_sales

GROUP BY store_id;



-------------------------------------------------------------
-- State Sales Summary
-------------------------------------------------------------

DROP TABLE IF EXISTS summary_state_sales;

CREATE TABLE summary_state_sales AS

SELECT

    s.state_id,

    SUM(f.sales) AS total_units_sold

FROM fact_daily_sales f

JOIN dim_store s
ON f.store_id = s.store_id

GROUP BY s.state_id;



-------------------------------------------------------------
-- Product Sales Summary
-------------------------------------------------------------

DROP TABLE IF EXISTS summary_product_sales;

CREATE TABLE summary_product_sales AS

SELECT

    item_id,

    SUM(sales) AS total_units_sold

FROM fact_daily_sales

GROUP BY item_id;



-------------------------------------------------------------
-- Category Sales Summary
-------------------------------------------------------------

DROP TABLE IF EXISTS summary_category_sales;

CREATE TABLE summary_category_sales AS

SELECT

    p.cat_id,

    SUM(f.sales) AS total_units_sold

FROM fact_daily_sales f

JOIN dim_product p
ON f.item_id = p.item_id

GROUP BY p.cat_id;



-------------------------------------------------------------
-- Monthly Sales Summary
-------------------------------------------------------------

DROP TABLE IF EXISTS summary_monthly_sales;

CREATE TABLE summary_monthly_sales AS

SELECT

    c.year,

    c.month,

    SUM(f.sales) AS total_units_sold

FROM fact_daily_sales f

JOIN dim_calendar c
ON f.date = c.date

GROUP BY

    c.year,
    c.month;