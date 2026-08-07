-- ==========================================================
-- RetailIQ SQL Warehouse
-- Create Indexes
-- ==========================================================

-- Calendar

CREATE INDEX IF NOT EXISTS idx_calendar_week
ON dim_calendar(wm_yr_wk);

CREATE INDEX IF NOT EXISTS idx_calendar_year
ON dim_calendar(year);

CREATE INDEX IF NOT EXISTS idx_calendar_month
ON dim_calendar(month);


-- Product

CREATE INDEX IF NOT EXISTS idx_product_category
ON dim_product(cat_id);

CREATE INDEX IF NOT EXISTS idx_product_department
ON dim_product(dept_id);


-- Store

CREATE INDEX IF NOT EXISTS idx_store_state
ON dim_store(state_id);


-- Prices

CREATE INDEX IF NOT EXISTS idx_prices_item
ON fact_sell_prices(item_id);

CREATE INDEX IF NOT EXISTS idx_prices_store
ON fact_sell_prices(store_id);

CREATE INDEX IF NOT EXISTS idx_prices_week
ON fact_sell_prices(wm_yr_wk);


-- Sales

CREATE INDEX IF NOT EXISTS idx_sales_item
ON fact_daily_sales(item_id);

CREATE INDEX IF NOT EXISTS idx_sales_store
ON fact_daily_sales(store_id);

CREATE INDEX IF NOT EXISTS idx_sales_date
ON fact_daily_sales(date);

CREATE INDEX IF NOT EXISTS idx_sales_week
ON fact_daily_sales(wm_yr_wk);