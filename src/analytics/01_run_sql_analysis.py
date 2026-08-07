from pathlib import Path
import sqlite3
import pandas as pd
import time


# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "database" / "RetailIQ.db"

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "query_results"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ==========================================================
# BUSINESS QUESTIONS
# ==========================================================

BUSINESS_QUERIES = {

    "top_stores": """
        SELECT
            store_id,
            total_units_sold,
            average_daily_sales
        FROM summary_store_sales
        ORDER BY total_units_sold DESC;
    """,

    "top_states": """
        SELECT
            state_id,
            total_units_sold
        FROM summary_state_sales
        ORDER BY total_units_sold DESC;
    """,

    "top_products": """
        SELECT
            item_id,
            total_units_sold
        FROM summary_product_sales
        ORDER BY total_units_sold DESC
        LIMIT 25;
    """,

    "category_sales": """
        SELECT
            cat_id,
            total_units_sold
        FROM summary_category_sales
        ORDER BY total_units_sold DESC;
    """,

    "monthly_sales": """
        SELECT
            year,
            month,
            total_units_sold
        FROM summary_monthly_sales
        ORDER BY year, month;
    """
}


# ==========================================================
# RUN QUERY
# ==========================================================

def run_query(
    connection,
    query_name,
    sql,
):

    print(f"\nRunning: {query_name}")

    dataframe = pd.read_sql_query(
        sql,
        connection,
    )

    # -----------------------------------------
    # Round all decimal columns
    # -----------------------------------------

    float_columns = dataframe.select_dtypes(
        include="float"
    ).columns

    dataframe[float_columns] = dataframe[
        float_columns
    ].round(2)

    # -----------------------------------------
    # Make column names nicer
    # -----------------------------------------

    dataframe.columns = [
        column.replace("_", " ").title()
        for column in dataframe.columns
    ]

    # -----------------------------------------
    # Save CSV
    # -----------------------------------------

    output_file = (
        OUTPUT_DIR
        / f"{query_name}.csv"
    )

    dataframe.to_csv(
        output_file,
        index=False,
    )

    print(f"Saved -> {output_file.name}")

    print("\nPreview:\n")

    print(dataframe.head())


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("=" * 60)
    print("RETAILIQ ANALYTICS ENGINE")
    print("=" * 60)

    start = time.time()

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    for (
        query_name,
        sql,
    ) in BUSINESS_QUERIES.items():

        run_query(
            connection,
            query_name,
            sql,
        )

    connection.close()

    elapsed = (
        time.time()
        - start
    )

    print(
        f"\nFinished in {elapsed:.2f} seconds"
    )


if __name__ == "__main__":
    main()