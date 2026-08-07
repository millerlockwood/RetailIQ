from pathlib import Path
import sqlite3
import pandas as pd
import time


# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "database" / "RetailIQ.db"

OUTPUT_DIR = PROJECT_ROOT / "reports"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ==========================================================
# KPI QUERIES
# ==========================================================

KPI_QUERIES = {

    "Total Units Sold": """
        SELECT
            SUM(total_units_sold)
        FROM summary_store_sales;
    """,

    "Number of Products": """
        SELECT
            COUNT(*)
        FROM dim_product;
    """,

    "Number of Stores": """
        SELECT
            COUNT(*)
        FROM dim_store;
    """,

    "Number of States": """
        SELECT
            COUNT(DISTINCT state_id)
        FROM dim_store;
    """,

    "Top Store": """
        SELECT
            store_id
        FROM summary_store_sales
        ORDER BY total_units_sold DESC
        LIMIT 1;
    """,

    "Top State": """
        SELECT
            state_id
        FROM summary_state_sales
        ORDER BY total_units_sold DESC
        LIMIT 1;
    """,

    "Top Product": """
        SELECT
            item_id
        FROM summary_product_sales
        ORDER BY total_units_sold DESC
        LIMIT 1;
    """,

    "Top Category": """
        SELECT
            cat_id
        FROM summary_category_sales
        ORDER BY total_units_sold DESC
        LIMIT 1;
    """
}


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("=" * 60)
    print("RETAILIQ EXECUTIVE KPI ENGINE")
    print("=" * 60)

    start = time.time()

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    kpis = []

    for (
        kpi_name,
        sql,
    ) in KPI_QUERIES.items():

        value = pd.read_sql_query(
            sql,
            connection,
        ).iloc[0, 0]

        # Make large numbers easier to read
        if isinstance(value, float):
            value = round(value, 2)

        kpis.append(
            {
                "KPI": kpi_name,
                "Value": value,
            }
        )

        print(f"{kpi_name}: {value}")

    connection.close()

    dataframe = pd.DataFrame(kpis)

    output_file = (
        OUTPUT_DIR
        / "executive_kpis.csv"
    )

    dataframe.to_csv(
        output_file,
        index=False,
    )

    elapsed = time.time() - start

    print("\nSaved -> executive_kpis.csv")

    print(f"\nCompleted in {elapsed:.2f} seconds")


if __name__ == "__main__":
    main()