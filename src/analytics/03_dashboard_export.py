from pathlib import Path
import sqlite3
import pandas as pd


# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "database" / "RetailIQ.db"

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "dashboard_data"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ==========================================================
# KPI QUERIES
# ==========================================================

KPI_QUERIES = {

    "kpi_total_units.csv": """
        SELECT
            SUM(total_units_sold) AS total_units_sold
        FROM summary_store_sales;
    """,

    "kpi_products.csv": """
        SELECT
            COUNT(*) AS number_of_products
        FROM dim_product;
    """,

    "kpi_stores.csv": """
        SELECT
            COUNT(*) AS number_of_stores
        FROM dim_store;
    """,

    "kpi_states.csv": """
        SELECT
            COUNT(DISTINCT state_id) AS number_of_states
        FROM dim_store;
    """,

    "kpi_top_store.csv": """
        SELECT
            store_id AS top_store
        FROM summary_store_sales
        ORDER BY total_units_sold DESC
        LIMIT 1;
    """,

    "kpi_top_state.csv": """
        SELECT
            state_id AS top_state
        FROM summary_state_sales
        ORDER BY total_units_sold DESC
        LIMIT 1;
    """,

    "kpi_top_product.csv": """
        SELECT
            item_id AS top_product
        FROM summary_product_sales
        ORDER BY total_units_sold DESC
        LIMIT 1;
    """,

    "kpi_top_category.csv": """
        SELECT
            cat_id AS top_category
        FROM summary_category_sales
        ORDER BY total_units_sold DESC
        LIMIT 1;
    """,
}


# ==========================================================
# DASHBOARD TABLE QUERIES
# ==========================================================

DASHBOARD_QUERIES = {

    "top_stores.csv": """
        SELECT
            store_id,
            total_units_sold,
            ROUND(average_daily_sales, 2) AS average_daily_sales
        FROM summary_store_sales
        ORDER BY total_units_sold DESC;
    """,

    "top_states.csv": """
        SELECT
            state_id,
            total_units_sold
        FROM summary_state_sales
        ORDER BY total_units_sold DESC;
    """,

    "top_products.csv": """
        SELECT
            item_id,
            total_units_sold
        FROM summary_product_sales
        ORDER BY total_units_sold DESC
        LIMIT 25;
    """,

    "category_sales.csv": """
        SELECT
            cat_id,
            total_units_sold
        FROM summary_category_sales
        ORDER BY total_units_sold DESC;
    """,

    "monthly_sales.csv": """
        SELECT
            year,
            month,
            total_units_sold
        FROM summary_monthly_sales
        ORDER BY year, month;
    """,
}


# ==========================================================
# EXPORT FUNCTION
# ==========================================================

def export_query(
    connection: sqlite3.Connection,
    filename: str,
    sql: str,
) -> None:
    """Run SQL and export the result to CSV."""

    dataframe = pd.read_sql_query(
        sql,
        connection,
    )

    output_path = (
        OUTPUT_DIR
        / filename
    )

    dataframe.to_csv(
        output_path,
        index=False,
    )

    print(
        f"✅ {filename}"
    )


# ==========================================================
# MAIN
# ==========================================================

def main() -> None:
    """Generate all Power BI dashboard datasets."""

    print("=" * 60)
    print("RETAILIQ DASHBOARD EXPORT")
    print("=" * 60)

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    try:

        print("\nExporting KPI files...")

        for filename, sql in KPI_QUERIES.items():

            export_query(
                connection,
                filename,
                sql,
            )

        print("\nExporting dashboard tables...")

        for filename, sql in DASHBOARD_QUERIES.items():

            export_query(
                connection,
                filename,
                sql,
            )

    finally:

        connection.close()

    print("\nDashboard export complete.")

    print(
        f"Output folder: {OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()