from pathlib import Path
import sqlite3
import time


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "database" / "RetailIQ.db"


SUMMARY_QUERIES = {
    "summary_store_sales": """
    DROP TABLE IF EXISTS summary_store_sales;

    CREATE TABLE summary_store_sales AS
    SELECT
        store_id,
        SUM(sales) AS total_units_sold,
        ROUND(
            SUM(sales) * 1.0 / COUNT(DISTINCT date),
            2
        ) AS average_daily_sales
    FROM fact_daily_sales
    GROUP BY store_id;
""",

    "summary_state_sales": """
        DROP TABLE IF EXISTS summary_state_sales;

        CREATE TABLE summary_state_sales AS
        SELECT
            s.state_id,
            SUM(f.sales) AS total_units_sold
        FROM fact_daily_sales f
        JOIN dim_store s
            ON f.store_id = s.store_id
        GROUP BY s.state_id;
    """,

    "summary_product_sales": """
        DROP TABLE IF EXISTS summary_product_sales;

        CREATE TABLE summary_product_sales AS
        SELECT
            item_id,
            SUM(sales) AS total_units_sold
        FROM fact_daily_sales
        GROUP BY item_id;
    """,

    "summary_category_sales": """
        DROP TABLE IF EXISTS summary_category_sales;

        CREATE TABLE summary_category_sales AS
        SELECT
            p.cat_id,
            SUM(f.sales) AS total_units_sold
        FROM fact_daily_sales f
        JOIN dim_product p
            ON f.item_id = p.item_id
        GROUP BY p.cat_id;
    """,

    "summary_monthly_sales": """
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
    """,
}


def get_row_count(
    connection: sqlite3.Connection,
    table_name: str,
) -> int:
    """Return the number of rows in a table."""

    cursor = connection.execute(
        f"SELECT COUNT(*) FROM {table_name}"
    )

    return cursor.fetchone()[0]


def main() -> None:
    """Create RetailIQ reporting summary tables."""

    print("=" * 60)
    print("RETAILIQ SUMMARY TABLE CREATION")
    print("=" * 60)

    connection = sqlite3.connect(DATABASE_PATH)

    overall_start = time.time()

    try:
        for table_name, sql in SUMMARY_QUERIES.items():

            print(f"\nCreating {table_name}...")

            start = time.time()

            connection.executescript(sql)

            connection.commit()

            row_count = get_row_count(
                connection,
                table_name,
            )

            elapsed = time.time() - start

            print(
                f"✅ {table_name}: "
                f"{row_count:,} rows "
                f"({elapsed:.1f} sec)"
            )

    finally:
        connection.close()

    total_elapsed = time.time() - overall_start

    print("\n" + "=" * 60)
    print("SUMMARY TABLE CREATION COMPLETE")
    print("=" * 60)

    print(
        f"\nTotal runtime: "
        f"{total_elapsed / 60:.2f} minutes"
    )


if __name__ == "__main__":
    main()     