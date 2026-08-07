-- ==========================================================
-- RetailIQ SQL Warehouse
-- Business Views
-- ==========================================================

-------------------------------------------------------------
-- Daily Sales
-------------------------------------------------------------

CREATE VIEW IF NOT EXISTS vw_daily_sales AS

SELECT

    c.date,
    c.year,
    c.month,
    c.weekday,

    f.item_id,
    p.cat_id,
    p.dept_id,

    f.store_id,
    s.state_id,

    f.sales

FROM fact_daily_sales f

JOIN dim_calendar c
ON f.date = c.date

JOIN dim_product p
ON f.item_id = p.item_id

JOIN dim_store s
ON f.store_id = s.store_id;



-------------------------------------------------------------
-- State Sales
-------------------------------------------------------------

CREATE VIEW IF NOT EXISTS vw_state_sales AS

SELECT

    s.state_id,

    SUM(f.sales) AS total_sales

FROM fact_daily_sales f

JOIN dim_store s
ON f.store_id = s.store_id

GROUP BY s.state_id;



-------------------------------------------------------------
-- Store Sales
-------------------------------------------------------------

CREATE VIEW IF NOT EXISTS vw_store_sales AS

SELECT

    store_id,

    SUM(sales) AS total_sales

FROM fact_daily_sales

GROUP BY store_id;



-------------------------------------------------------------
-- Product Sales
-------------------------------------------------------------

CREATE VIEW IF NOT EXISTS vw_product_sales AS

SELECT

    item_id,

    SUM(sales) AS total_sales

FROM fact_daily_sales

GROUP BY item_id;



-------------------------------------------------------------
-- Category Sales
-------------------------------------------------------------

CREATE VIEW IF NOT EXISTS vw_category_sales AS

SELECT

    p.cat_id,

    SUM(f.sales) AS total_sales

FROM fact_daily_sales f

JOIN dim_product p
ON f.item_id = p.item_id

GROUP BY p.cat_id;