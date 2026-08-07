from pathlib import Path
import sqlite3

import pandas as pd


# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = (
    PROJECT_ROOT
    / "database"
    / "RetailIQ.db"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "forecasting"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "weekly_store_sales.parquet"
)


# ==========================================================
# SQL QUERY
# ==========================================================

FORECAST_QUERY = """
SELECT
    f.store_id,
    f.wm_yr_wk,
    MIN(f.date) AS week_start_date,
    SUM(f.sales) AS weekly_units_sold
FROM fact_daily_sales f
GROUP BY
    f.store_id,
    f.wm_yr_wk
ORDER BY
    f.store_id,
    f.wm_yr_wk;
"""


# ==========================================================
# MAIN
# ==========================================================

def main() -> None:
    """Prepare true weekly store-level demand data."""

    print("=" * 60)
    print("RETAILIQ FORECAST DATA PREPARATION")
    print("=" * 60)

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    try:

        print(
            "\nAggregating daily sales into true weekly demand..."
        )

        dataframe = pd.read_sql_query(
            FORECAST_QUERY,
            connection,
        )

    finally:

        connection.close()

    # ------------------------------------------------------
    # DATE FEATURES
    # ------------------------------------------------------

    dataframe["week_start_date"] = pd.to_datetime(
        dataframe["week_start_date"]
    )

    dataframe["year"] = (
        dataframe["week_start_date"]
        .dt
        .year
    )

    dataframe["month"] = (
        dataframe["week_start_date"]
        .dt
        .month
    )

    dataframe = dataframe.sort_values(
        [
            "store_id",
            "week_start_date",
        ]
    ).reset_index(drop=True)

    # ------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------

    duplicate_weeks = dataframe.duplicated(
        subset=[
            "store_id",
            "wm_yr_wk",
        ]
    ).sum()

    if duplicate_weeks != 0:
        raise ValueError(
            f"Detected {duplicate_weeks:,} duplicate "
            "store-week records."
        )

    # ------------------------------------------------------
    # SAVE
    # ------------------------------------------------------

    dataframe.to_parquet(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"\nRows created: {len(dataframe):,}"
    )

    print(
        f"Stores: {dataframe['store_id'].nunique():,}"
    )

    print(
        f"Unique weeks: "
        f"{dataframe['wm_yr_wk'].nunique():,}"
    )

    print(
        f"Duplicate store-weeks: "
        f"{duplicate_weeks:,}"
    )

    print(
        f"Date range: "
        f"{dataframe['week_start_date'].min().date()} "
        f"to "
        f"{dataframe['week_start_date'].max().date()}"
    )

    print(
        f"\nSaved -> {OUTPUT_PATH}"
    )

    print(
        "\nForecasting dataset preparation complete."
    )


if __name__ == "__main__":
    main()