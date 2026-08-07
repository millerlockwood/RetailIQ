SELECT
    store_id,
    SUM(sales) AS total_units_sold
FROM fact_daily_sales
GROUP BY store_id
ORDER BY total_units_sold DESC;