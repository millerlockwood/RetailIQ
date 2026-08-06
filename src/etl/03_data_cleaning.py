from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORT_PATH = REPORTS_DIR / "03_Cleaning_Report.md"


def memory_usage_mb(dataframe: pd.DataFrame) -> float:
    """Return total DataFrame memory usage in megabytes."""

    return dataframe.memory_usage(deep=True).sum() / 1024**2


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load the raw RetailIQ datasets."""

    print("Loading raw datasets...")

    calendar = pd.read_csv(
        RAW_DATA_DIR / "calendar.csv",
        low_memory=False,
    )

    sales = pd.read_csv(
        RAW_DATA_DIR / "sales_train_validation.csv",
        low_memory=False,
    )

    prices = pd.read_csv(
        RAW_DATA_DIR / "sell_prices.csv",
        low_memory=False,
    )

    return calendar, sales, prices


def clean_calendar(
    calendar: pd.DataFrame,
) -> tuple[pd.DataFrame, list[str]]:
    """Clean and optimize the calendar dataset."""

    cleaned = calendar.copy()
    actions = []

    cleaned["date"] = pd.to_datetime(
        cleaned["date"],
        errors="raise",
    )
    actions.append("Converted `date` to datetime.")

    event_columns = [
        "event_name_1",
        "event_type_1",
        "event_name_2",
        "event_type_2",
    ]

    for column in event_columns:
        cleaned[column] = cleaned[column].fillna("No Event")
        cleaned[column] = cleaned[column].astype("category")

    actions.append(
        "Replaced expected event-column nulls with `No Event`."
    )
    actions.append(
        "Converted event names and event types to categorical data."
    )

    category_columns = [
        "weekday",
        "d",
    ]

    for column in category_columns:
        cleaned[column] = cleaned[column].astype("category")

    actions.append(
        "Converted weekday and day identifier columns to categorical data."
    )

    integer_columns = [
        "wm_yr_wk",
        "wday",
        "month",
        "year",
        "snap_CA",
        "snap_TX",
        "snap_WI",
    ]

    for column in integer_columns:
        cleaned[column] = pd.to_numeric(
            cleaned[column],
            downcast="unsigned",
        )

    actions.append(
        "Downcast calendar integer columns to smaller unsigned types."
    )

    return cleaned, actions


def clean_sales(
    sales: pd.DataFrame,
) -> tuple[pd.DataFrame, list[str]]:
    """Clean and optimize the wide sales dataset."""

    cleaned = sales.copy()
    actions = []

    identifier_columns = [
        "id",
        "item_id",
        "dept_id",
        "cat_id",
        "store_id",
        "state_id",
    ]

    for column in identifier_columns:
        cleaned[column] = cleaned[column].astype("category")

    actions.append(
        "Converted sales identifier columns to categorical data."
    )

    sales_columns = [
        column
        for column in cleaned.columns
        if column.startswith("d_")
    ]

    for column in sales_columns:
        cleaned[column] = pd.to_numeric(
            cleaned[column],
            downcast="unsigned",
        )

    actions.append(
        f"Downcast {len(sales_columns):,} daily sales columns "
        "to smaller unsigned integer types."
    )

    return cleaned, actions


def clean_prices(
    prices: pd.DataFrame,
) -> tuple[pd.DataFrame, list[str]]:
    """Clean and optimize the selling-price dataset."""

    cleaned = prices.copy()
    actions = []

    for column in ["store_id", "item_id"]:
        cleaned[column] = cleaned[column].astype("category")

    actions.append(
        "Converted store and item identifiers to categorical data."
    )

    cleaned["wm_yr_wk"] = pd.to_numeric(
        cleaned["wm_yr_wk"],
        downcast="unsigned",
    )

    cleaned["sell_price"] = pd.to_numeric(
        cleaned["sell_price"],
        downcast="float",
    )

    actions.append(
        "Downcast week identifiers and selling prices."
    )

    return cleaned, actions


def validate_cleaning(
    original: pd.DataFrame,
    cleaned: pd.DataFrame,
    dataset_name: str,
) -> list[str]:
    """Confirm cleaning did not alter the dataset structure incorrectly."""

    checks = []

    if len(original) != len(cleaned):
        raise ValueError(
            f"{dataset_name}: Row count changed during cleaning."
        )

    checks.append(
        f"{dataset_name}: Row count preserved at {len(cleaned):,}."
    )

    if list(original.columns) != list(cleaned.columns):
        raise ValueError(
            f"{dataset_name}: Column structure changed during cleaning."
        )

    checks.append(
        f"{dataset_name}: Column names and order were preserved."
    )

    return checks


def save_processed_data(
    calendar: pd.DataFrame,
    sales: pd.DataFrame,
    prices: pd.DataFrame,
) -> dict[str, Path]:
    """Save cleaned datasets as compressed Parquet files."""

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_paths = {
        "Calendar": PROCESSED_DATA_DIR / "calendar_clean.parquet",
        "Sales": PROCESSED_DATA_DIR / "sales_clean.parquet",
        "Prices": PROCESSED_DATA_DIR / "sell_prices_clean.parquet",
    }

    print("Saving processed datasets...")

    calendar.to_parquet(
        output_paths["Calendar"],
        index=False,
        compression="snappy",
    )

    sales.to_parquet(
        output_paths["Sales"],
        index=False,
        compression="snappy",
    )

    prices.to_parquet(
        output_paths["Prices"],
        index=False,
        compression="snappy",
    )

    return output_paths


def generate_cleaning_report(
    dataset_results: list[dict],
    output_paths: dict[str, Path],
) -> None:
    """Generate the Markdown cleaning report."""

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    total_before = sum(
        result["memory_before"]
        for result in dataset_results
    )

    total_after = sum(
        result["memory_after"]
        for result in dataset_results
    )

    reduction_mb = total_before - total_after
    reduction_percent = (
        reduction_mb / total_before * 100
        if total_before
        else 0
    )

    report_lines = [
        "# RetailIQ Cleaning Report",
        "",
        "## Executive Summary",
        "",
        "- Cleaning status: **COMPLETED**",
        f"- Total memory before: **{total_before:,.2f} MB**",
        f"- Total memory after: **{total_after:,.2f} MB**",
        f"- Memory reduction: **{reduction_mb:,.2f} MB**",
        f"- Percentage reduction: **{reduction_percent:.2f}%**",
        "",
        "## Dataset Summary",
        "",
        "| Dataset | Rows | Memory Before | Memory After | Reduction |",
        "|---|---:|---:|---:|---:|",
    ]

    for result in dataset_results:
        dataset_reduction = (
            result["memory_before"]
            - result["memory_after"]
        )

        report_lines.append(
            f"| {result['name']} | "
            f"{result['rows']:,} | "
            f"{result['memory_before']:.2f} MB | "
            f"{result['memory_after']:.2f} MB | "
            f"{dataset_reduction:.2f} MB |"
        )

    for result in dataset_results:
        report_lines.extend(
            [
                "",
                f"## {result['name']}",
                "",
                "### Cleaning Actions",
                "",
            ]
        )

        for action in result["actions"]:
            report_lines.append(f"- {action}")

        report_lines.extend(
            [
                "",
                "### Validation Checks",
                "",
            ]
        )

        for check in result["checks"]:
            report_lines.append(f"- {check}")

        report_lines.extend(
            [
                "",
                "### Output",
                "",
                f"- `{output_paths[result['name']]}`",
            ]
        )

    report_lines.extend(
        [
            "",
            "## Recommendation",
            "",
            "The processed datasets are ready for transformation into "
            "analytics-ready tables and loading into the SQL warehouse.",
        ]
    )

    REPORT_PATH.write_text(
        "\n".join(report_lines),
        encoding="utf-8",
    )


def main() -> None:
    """Run the complete RetailIQ cleaning workflow."""

    print("=" * 60)
    print("RETAILIQ DATA CLEANING")
    print("=" * 60)

    calendar_raw, sales_raw, prices_raw = load_data()

    dataset_results = []

    print("Cleaning Calendar...")
    calendar_clean, calendar_actions = clean_calendar(
        calendar_raw
    )
    calendar_checks = validate_cleaning(
        calendar_raw,
        calendar_clean,
        "Calendar",
    )

    dataset_results.append(
        {
            "name": "Calendar",
            "rows": len(calendar_clean),
            "memory_before": memory_usage_mb(calendar_raw),
            "memory_after": memory_usage_mb(calendar_clean),
            "actions": calendar_actions,
            "checks": calendar_checks,
        }
    )

    print("Cleaning Sales...")
    sales_clean, sales_actions = clean_sales(
        sales_raw
    )
    sales_checks = validate_cleaning(
        sales_raw,
        sales_clean,
        "Sales",
    )

    dataset_results.append(
        {
            "name": "Sales",
            "rows": len(sales_clean),
            "memory_before": memory_usage_mb(sales_raw),
            "memory_after": memory_usage_mb(sales_clean),
            "actions": sales_actions,
            "checks": sales_checks,
        }
    )

    print("Cleaning Sell Prices...")
    prices_clean, prices_actions = clean_prices(
        prices_raw
    )
    prices_checks = validate_cleaning(
        prices_raw,
        prices_clean,
        "Prices",
    )

    dataset_results.append(
        {
            "name": "Prices",
            "rows": len(prices_clean),
            "memory_before": memory_usage_mb(prices_raw),
            "memory_after": memory_usage_mb(prices_clean),
            "actions": prices_actions,
            "checks": prices_checks,
        }
    )

    output_paths = save_processed_data(
        calendar_clean,
        sales_clean,
        prices_clean,
    )

    generate_cleaning_report(
        dataset_results,
        output_paths,
    )

    print("\nCLEANING SUMMARY")
    print("-" * 60)

    for result in dataset_results:
        reduction = (
            result["memory_before"]
            - result["memory_after"]
        )

        print(
            f"{result['name']}: "
            f"{result['memory_before']:.2f} MB -> "
            f"{result['memory_after']:.2f} MB "
            f"({reduction:.2f} MB reduced)"
        )

    print("\nProcessed datasets created:")
    for path in output_paths.values():
        print(path)

    print("\nCleaning report created:")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()