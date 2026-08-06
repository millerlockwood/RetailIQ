-- ==========================================================
-- RetailIQ SQL Warehouse
-- Create Tables
-- ==========================================================

PRAGMA foreign_keys = ON;

-- ==========================================================
-- Calendar Dimension
-- ==========================================================

CREATE TABLE IF NOT EXISTS dim_calendar (

    date TEXT PRIMARY KEY,

    d TEXT UNIQUE,

    wm_yr_wk INTEGER,

    weekday TEXT,

    wday INTEGER,

    month INTEGER,

    year INTEGER,

    event_name_1 TEXT,

    event_type_1 TEXT,

    event_name_2 TEXT,

    event_type_2 TEXT,

    snap_CA INTEGER,

    snap_TX INTEGER,

    snap_WI INTEGER

);

-- ==========================================================
-- Product Dimension
-- ==========================================================

CREATE TABLE IF NOT EXISTS dim_product (

    item_id TEXT PRIMARY KEY,

    dept_id TEXT,

    cat_id TEXT

);

-- ==========================================================
-- Store Dimension
-- ==========================================================

CREATE TABLE IF NOT EXISTS dim_store (

    store_id TEXT PRIMARY KEY,

    state_id TEXT

);

-- ==========================================================
-- Daily Sales Fact
-- ==========================================================

CREATE TABLE IF NOT EXISTS fact_daily_sales (

    date TEXT,

    item_id TEXT,

    store_id TEXT,

    wm_yr_wk INTEGER,

    sales INTEGER,

    PRIMARY KEY (

        date,

        item_id,

        store_id

    ),

    FOREIGN KEY(date)
        REFERENCES dim_calendar(date),

    FOREIGN KEY(item_id)
        REFERENCES dim_product(item_id),

    FOREIGN KEY(store_id)
        REFERENCES dim_store(store_id)

);

-- ==========================================================
-- Weekly Prices Fact
-- ==========================================================

CREATE TABLE IF NOT EXISTS fact_sell_prices (

    wm_yr_wk INTEGER,

    item_id TEXT,

    store_id TEXT,

    sell_price REAL,

    PRIMARY KEY (

        wm_yr_wk,

        item_id,

        store_id

    ),

    FOREIGN KEY(item_id)
        REFERENCES dim_product(item_id),

    FOREIGN KEY(store_id)
        REFERENCES dim_store(store_id)

);