# RetailIQ Cleaning Report

## Executive Summary

- Cleaning status: **COMPLETED**
- Total memory before: **766.63 MB**
- Total memory after: **123.66 MB**
- Memory reduction: **642.97 MB**
- Percentage reduction: **83.87%**

## Dataset Summary

| Dataset | Rows | Memory Before | Memory After | Reduction |
|---|---:|---:|---:|---:|
| Calendar | 1,969 | 0.26 MB | 0.07 MB | 0.19 MB |
| Sales | 30,490 | 448.23 MB | 64.81 MB | 383.42 MB |
| Prices | 6,841,121 | 318.15 MB | 58.78 MB | 259.37 MB |

## Calendar

### Cleaning Actions

- Converted `date` to datetime.
- Replaced expected event-column nulls with `No Event`.
- Converted event names and event types to categorical data.
- Converted weekday and day identifier columns to categorical data.
- Downcast calendar integer columns to smaller unsigned types.

### Validation Checks

- Calendar: Row count preserved at 1,969.
- Calendar: Column names and order were preserved.

### Output

- `C:\Projects\RetailIQ\data\processed\calendar_clean.parquet`

## Sales

### Cleaning Actions

- Converted sales identifier columns to categorical data.
- Downcast 1,913 daily sales columns to smaller unsigned integer types.

### Validation Checks

- Sales: Row count preserved at 30,490.
- Sales: Column names and order were preserved.

### Output

- `C:\Projects\RetailIQ\data\processed\sales_clean.parquet`

## Prices

### Cleaning Actions

- Converted store and item identifiers to categorical data.
- Downcast week identifiers and selling prices.

### Validation Checks

- Prices: Row count preserved at 6,841,121.
- Prices: Column names and order were preserved.

### Output

- `C:\Projects\RetailIQ\data\processed\sell_prices_clean.parquet`

## Recommendation

The processed datasets are ready for transformation into analytics-ready tables and loading into the SQL warehouse.