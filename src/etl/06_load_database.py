from pathlib import Path
import sqlite3
import time

import pandas as pd


# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "database" / "RetailIQ.db"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


# ==========================================================
# DATABASE HELPERS
# ==========================================================

def get_row_count(
    connection: sqlite3.Connection,
    table_name: str,
) -> int:
    """Return the number of rows currently stored in a table."""

    cursor = connection.cursor()

    cursor.execute(
        f"SELECT COUNT(*) FROM {table_name}"
    )

    return cursor.fetchone()[0]


def verify_existing_load(
    connection: sqlite3.Connection,
    table_name: str,
    expected_rows: int,
) -> bool:
    """
    Check whether a table is already fully loaded.

    Returns True if the table is complete.
    Raises an error if a partial load is detected.
    """

    existing_rows = get_row_count(
        connection,
        table_name,
    )

    if existing_rows == 0:
        return False

    if existing_rows == expected_rows:
        print(
            f"⏭ {table_name} already loaded: "
            f"{existing_rows:,} rows"
        )

        return True

    raise RuntimeError(
        f"{table_name} contains a partial load. "
        f"Expected {expected_rows:,} rows but found "
        f"{existing_rows:,}. Clear the table before rerunning."
    )


# ==========================================================
# LOAD SOURCE DATA
# ==========================================================

def load_source_data():
    """Load processed RetailIQ datasets."""

    print("\nLoading processed datasets...")

    calendar = pd.read_parquet(
        PROCESSED_DIR / "calendar_clean.parquet"
    )

    product_source = pd.read_parquet(
        PROCESSED_DIR / "sales_clean.parquet"
    )

    prices = pd.read_parquet(
        PROCESSED_DIR / "sell_prices_clean.parquet"
    )

    daily_sales = pd.read_parquet(
        PROCESSED_DIR / "daily_sales_long.parquet"
    )

    print(
        f"Calendar source rows: {len(calendar):,}"
    )

    print(
        f"Product source rows: {len(product_source):,}"
    )

    print(
        f"Price source rows: {len(prices):,}"
    )

    print(
        f"Daily sales source rows: {len(daily_sales):,}"
    )

    return (
        calendar,
        product_source,
        prices,
        daily_sales,
    )


# ==========================================================
# CREATE DIMENSIONS
# ==========================================================

def create_product_dimension(
    product_source: pd.DataFrame,
) -> pd.DataFrame:
    """Create one record per product."""

    return (
        product_source[
            [
                "item_id",
                "dept_id",
                "cat_id",
            ]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )


def create_store_dimension(
    product_source: pd.DataFrame,
) -> pd.DataFrame:
    """Create one record per store."""

    return (
        product_source[
            [
                "store_id",
                "state_id",
            ]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )


# ==========================================================
# LOAD CALENDAR DIMENSION
# ==========================================================

def load_calendar_dimension(
    connection: sqlite3.Connection,
    calendar: pd.DataFrame,
) -> None:
    """Load dim_calendar."""

    if verify_existing_load(
        connection,
        "dim_calendar",
        len(calendar),
    ):
        return

    calendar.to_sql(
        "dim_calendar",
        connection,
        if_exists="append",
        index=False,
    )

    connection.commit()

    print(
        f"✅ dim_calendar loaded: "
        f"{len(calendar):,} rows"
    )


# ==========================================================
# LOAD PRODUCT DIMENSION
# ==========================================================

def load_product_dimension(
    connection: sqlite3.Connection,
    product_dimension: pd.DataFrame,
) -> None:
    """Load dim_product."""

    if verify_existing_load(
        connection,
        "dim_product",
        len(product_dimension),
    ):
        return

    product_dimension.to_sql(
        "dim_product",
        connection,
        if_exists="append",
        index=False,
    )

    connection.commit()

    print(
        f"✅ dim_product loaded: "
        f"{len(product_dimension):,} rows"
    )


# ==========================================================
# LOAD STORE DIMENSION
# ==========================================================

def load_store_dimension(
    connection: sqlite3.Connection,
    store_dimension: pd.DataFrame,
) -> None:
    """Load dim_store."""

    if verify_existing_load(
        connection,
        "dim_store",
        len(store_dimension),
    ):
        return

    store_dimension.to_sql(
        "dim_store",
        connection,
        if_exists="append",
        index=False,
    )

    connection.commit()

    print(
        f"✅ dim_store loaded: "
        f"{len(store_dimension):,} rows"
    )


# ==========================================================
# LOAD PRICE FACT TABLE
# ==========================================================

def load_price_fact(
    connection: sqlite3.Connection,
    prices: pd.DataFrame,
) -> None:
    """Load fact_sell_prices."""

    print("\nLoading fact_sell_prices...")

    price_fact = prices[
        [
            "wm_yr_wk",
            "item_id",
            "store_id",
            "sell_price",
        ]
    ].copy()

    if verify_existing_load(
        connection,
        "fact_sell_prices",
        len(price_fact),
    ):
        return

    price_fact.to_sql(
        "fact_sell_prices",
        connection,
        if_exists="append",
        index=False,
        chunksize=10_000,
    )

    connection.commit()

    final_rows = get_row_count(
        connection,
        "fact_sell_prices",
    )

    if final_rows != len(price_fact):
        raise RuntimeError(
            "fact_sell_prices row-count validation failed."
        )

    print(
        f"✅ fact_sell_prices loaded: "
        f"{final_rows:,} rows"
    )


# ==========================================================
# LOAD DAILY SALES FACT TABLE
# ==========================================================

def load_daily_sales_fact(
    connection: sqlite3.Connection,
    daily_sales: pd.DataFrame,
) -> None:
    """Load fact_daily_sales using controlled chunks."""

    print("\nLoading fact_daily_sales...")

    sales_fact = daily_sales[
        [
            "date",
            "item_id",
            "store_id",
            "wm_yr_wk",
            "sales",
        ]
    ].copy()

    total_rows = len(sales_fact)

    if verify_existing_load(
        connection,
        "fact_daily_sales",
        total_rows,
    ):
        return

    chunk_size = 500_000

    total_chunks = (
        total_rows + chunk_size - 1
    ) // chunk_size

    load_start = time.time()

    for chunk_number, start_row in enumerate(
        range(0, total_rows, chunk_size),
        start=1,
    ):
        end_row = min(
            start_row + chunk_size,
            total_rows,
        )

        chunk = sales_fact.iloc[
            start_row:end_row
        ]

        chunk.to_sql(
            "fact_daily_sales",
            connection,
            if_exists="append",
            index=False,
            chunksize=10_000,
        )

        connection.commit()

        elapsed = time.time() - load_start

        percent_complete = (
            end_row / total_rows * 100
        )

        print(
            f"Chunk {chunk_number}/{total_chunks} | "
            f"{end_row:,}/{total_rows:,} rows | "
            f"{percent_complete:.1f}% | "
            f"{elapsed:.1f} sec"
        )

    final_rows = get_row_count(
        connection,
        "fact_daily_sales",
    )

    if final_rows != total_rows:
        raise RuntimeError(
            "fact_daily_sales row-count validation failed. "
            f"Expected {total_rows:,} rows but found "
            f"{final_rows:,}."
        )

    print(
        f"\n✅ fact_daily_sales loaded: "
        f"{final_rows:,} rows"
    )


# ==========================================================
# DATABASE SUMMARY
# ==========================================================

def print_database_summary(
    connection: sqlite3.Connection,
) -> None:
    """Print final warehouse row counts."""

    print("\nDATABASE LOAD SUMMARY")
    print("-" * 60)

    tables = [
        "dim_calendar",
        "dim_product",
        "dim_store",
        "fact_sell_prices",
        "fact_daily_sales",
    ]

    total_rows = 0

    for table in tables:
        row_count = get_row_count(
            connection,
            table,
        )

        total_rows += row_count

        print(
            f"{table}: {row_count:,} rows"
        )

    print("-" * 60)

    print(
        f"Total warehouse rows: "
        f"{total_rows:,}"
    )


# ==========================================================
# MAIN WORKFLOW
# ==========================================================

def main() -> None:
    """Run the complete RetailIQ database load."""

    print("=" * 60)
    print("RETAILIQ DATABASE LOADER")
    print("=" * 60)

    overall_start = time.time()

    (
        calendar,
        product_source,
        prices,
        daily_sales,
    ) = load_source_data()

    product_dimension = create_product_dimension(
        product_source
    )

    store_dimension = create_store_dimension(
        product_source
    )

    print(
        f"\nProduct dimension rows: "
        f"{len(product_dimension):,}"
    )

    print(
        f"Store dimension rows: "
        f"{len(store_dimension):,}"
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    # Enable referential-integrity enforcement.
    connection.execute(
        "PRAGMA foreign_keys = ON;"
    )

    # Improve bulk-load performance while maintaining
    # reasonable database safety.
    connection.execute(
        "PRAGMA journal_mode = WAL;"
    )

    connection.execute(
        "PRAGMA synchronous = NORMAL;"
    )

    connection.execute(
        "PRAGMA temp_store = MEMORY;"
    )

    print("\nDatabase connected.")

    try:

        print("\nLoading dimension tables...")

        load_calendar_dimension(
            connection,
            calendar,
        )

        load_product_dimension(
            connection,
            product_dimension,
        )

        load_store_dimension(
            connection,
            store_dimension,
        )

        load_price_fact(
            connection,
            prices,
        )

        load_daily_sales_fact(
            connection,
            daily_sales,
        )

        print_database_summary(
            connection
        )

    finally:

        connection.close()

    total_elapsed = (
        time.time() - overall_start
    )

    print(
        f"\nDatabase connection closed."
    )

    print(
        f"Total runtime: "
        f"{total_elapsed / 60:.2f} minutes"
    )

    print(
        "\nWarehouse Load Complete"
    )


if __name__ == "__main__":
    main()