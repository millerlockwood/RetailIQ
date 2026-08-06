from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORT_PATH = REPORTS_DIR / "02_Validation_Report.md"


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load the primary RetailIQ datasets."""

    calendar = pd.read_csv(RAW_DATA_DIR / "calendar.csv")
    sales = pd.read_csv(RAW_DATA_DIR / "sales_train_validation.csv")
    prices = pd.read_csv(RAW_DATA_DIR / "sell_prices.csv")

    return calendar, sales, prices


def create_result(
    category: str,
    check_name: str,
    passed: bool,
    message: str,
    severity: str = "High",
) -> dict:
    """Create a structured validation result."""

    return {
        "category": category,
        "check_name": check_name,
        "passed": passed,
        "message": message,
        "severity": severity,
    }


def validate_duplicates(
    dataframe: pd.DataFrame,
    name: str,
) -> dict:
    """Check for fully duplicated rows."""

    duplicate_count = int(dataframe.duplicated().sum())
    passed = duplicate_count == 0

    if passed:
        message = f"{name}: No duplicate rows"
    else:
        message = f"{name}: {duplicate_count:,} duplicate rows"

    return create_result(
        category="Dataset Checks",
        check_name=f"{name} duplicate rows",
        passed=passed,
        message=message,
    )


def validate_missing(
    dataframe: pd.DataFrame,
    name: str,
) -> dict:
    """Check for missing values."""

    missing_count = int(dataframe.isna().sum().sum())

    if name == "Calendar":
        expected_columns = {
            "event_name_1",
            "event_type_1",
            "event_name_2",
            "event_type_2",
        }

        unexpected_missing = int(
            dataframe.drop(
                columns=[
                    column
                    for column in expected_columns
                    if column in dataframe.columns
                ]
            )
            .isna()
            .sum()
            .sum()
        )

        passed = unexpected_missing == 0

        if passed:
            message = (
                f"{name}: {missing_count:,} expected missing values "
                "in event columns; no unexpected missing values"
            )
        else:
            message = (
                f"{name}: {unexpected_missing:,} unexpected missing values"
            )
    else:
        passed = missing_count == 0

        if passed:
            message = f"{name}: No missing values"
        else:
            message = f"{name}: {missing_count:,} missing values"

    return create_result(
        category="Missing-Value Checks",
        check_name=f"{name} missing values",
        passed=passed,
        message=message,
        severity="Medium",
    )


def validate_negative_prices(prices: pd.DataFrame) -> dict:
    """Check for negative selling prices."""

    negative_count = int((prices["sell_price"] < 0).sum())
    passed = negative_count == 0

    if passed:
        message = "Sell Prices: No negative prices"
    else:
        message = f"Sell Prices: {negative_count:,} negative prices"

    return create_result(
        category="Business-Rule Checks",
        check_name="Negative selling prices",
        passed=passed,
        message=message,
    )


def validate_sales_values(sales: pd.DataFrame) -> dict:
    """Check daily sales columns for negative values."""

    sales_columns = [
        column for column in sales.columns if column.startswith("d_")
    ]

    negative_count = int(
        (sales[sales_columns] < 0).sum().sum()
    )
    passed = negative_count == 0

    if passed:
        message = "Sales: No negative sales"
    else:
        message = f"Sales: {negative_count:,} negative sales values"

    return create_result(
        category="Business-Rule Checks",
        check_name="Negative sales values",
        passed=passed,
        message=message,
    )


def validate_calendar_weeks(
    calendar: pd.DataFrame,
    prices: pd.DataFrame,
) -> dict:
    """Verify every pricing week exists in the calendar."""

    missing_weeks = (
        set(prices["wm_yr_wk"])
        - set(calendar["wm_yr_wk"])
    )
    passed = len(missing_weeks) == 0

    if passed:
        message = "All pricing weeks exist in Calendar"
    else:
        message = (
            f"{len(missing_weeks):,} pricing weeks "
            "do not exist in Calendar"
        )

    return create_result(
        category="Relationship Checks",
        check_name="Calendar-pricing week relationship",
        passed=passed,
        message=message,
    )


def validate_price_items_exist_in_sales(
    sales: pd.DataFrame,
    prices: pd.DataFrame,
) -> dict:
    """Verify every priced item exists in the sales dataset."""

    missing_items = (
        set(prices["item_id"])
        - set(sales["item_id"])
    )
    passed = len(missing_items) == 0

    if passed:
        message = "All priced items exist in Sales"
    else:
        message = (
            f"{len(missing_items):,} priced items "
            "do not exist in Sales"
        )

    return create_result(
        category="Relationship Checks",
        check_name="Price-item relationship",
        passed=passed,
        message=message,
    )


def validate_price_stores_exist_in_sales(
    sales: pd.DataFrame,
    prices: pd.DataFrame,
) -> dict:
    """Verify every priced store exists in the sales dataset."""

    missing_stores = (
        set(prices["store_id"])
        - set(sales["store_id"])
    )
    passed = len(missing_stores) == 0

    if passed:
        message = "All priced stores exist in Sales"
    else:
        message = (
            f"{len(missing_stores):,} priced stores "
            "do not exist in Sales"
        )

    return create_result(
        category="Relationship Checks",
        check_name="Price-store relationship",
        passed=passed,
        message=message,
    )


def validate_product_store_pairs(
    sales: pd.DataFrame,
    prices: pd.DataFrame,
) -> dict:
    """Verify every priced product-store pair exists in Sales."""

    sales_pairs = set(
        zip(sales["store_id"], sales["item_id"])
    )

    price_pairs = set(
        zip(prices["store_id"], prices["item_id"])
    )

    missing_pairs = price_pairs - sales_pairs
    passed = len(missing_pairs) == 0

    if passed:
        message = (
            "All priced product-store pairs exist in Sales"
        )
    else:
        message = (
            f"{len(missing_pairs):,} priced product-store pairs "
            "do not exist in Sales"
        )

    return create_result(
        category="Relationship Checks",
        check_name="Product-store pair relationship",
        passed=passed,
        message=message,
    )


def validate_price_business_keys(
    prices: pd.DataFrame,
) -> dict:
    """Check uniqueness of store, item, and week in Sell Prices."""

    key_columns = ["store_id", "item_id", "wm_yr_wk"]

    duplicate_key_count = int(
        prices.duplicated(subset=key_columns).sum()
    )
    passed = duplicate_key_count == 0

    if passed:
        message = "Prices: No duplicate business keys"
    else:
        message = (
            f"Prices: {duplicate_key_count:,} duplicate "
            "store-item-week keys"
        )

    return create_result(
        category="Relationship Checks",
        check_name="Price business-key uniqueness",
        passed=passed,
        message=message,
    )


def run_validations(
    calendar: pd.DataFrame,
    sales: pd.DataFrame,
    prices: pd.DataFrame,
) -> list[dict]:
    """Run all RetailIQ validation checks."""

    return [
        validate_duplicates(calendar, "Calendar"),
        validate_duplicates(sales, "Sales"),
        validate_duplicates(prices, "Prices"),
        validate_missing(calendar, "Calendar"),
        validate_missing(sales, "Sales"),
        validate_missing(prices, "Prices"),
        validate_negative_prices(prices),
        validate_sales_values(sales),
        validate_calendar_weeks(calendar, prices),
        validate_price_items_exist_in_sales(sales, prices),
        validate_price_stores_exist_in_sales(sales, prices),
        validate_product_store_pairs(sales, prices),
        validate_price_business_keys(prices),
    ]


def print_results(results: list[dict]) -> None:
    """Print validation results to the terminal."""

    print("=" * 60)
    print("RETAILIQ DATA VALIDATION")
    print("=" * 60)

    categories = [
        "Dataset Checks",
        "Missing-Value Checks",
        "Business-Rule Checks",
        "Relationship Checks",
    ]

    for category in categories:
        print(f"\n{category.upper()}")
        print("-" * 60)

        for result in results:
            if result["category"] != category:
                continue

            symbol = "✅" if result["passed"] else "❌"
            print(f"{symbol} {result['message']}")

    passed_count = sum(result["passed"] for result in results)
    failed_count = len(results) - passed_count
    pipeline_status = "PASSED" if failed_count == 0 else "FAILED"

    print("\nPIPELINE STATUS")
    print("-" * 60)
    print(f"Status: {pipeline_status}")
    print(f"Checks passed: {passed_count}")
    print(f"Checks failed: {failed_count}")


def generate_report(results: list[dict]) -> None:
    """Generate the Markdown validation report."""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    passed_count = sum(result["passed"] for result in results)
    failed_count = len(results) - passed_count
    total_count = len(results)

    validation_score = round(
        passed_count / total_count * 100
    )
    pipeline_status = "PASSED" if failed_count == 0 else "FAILED"

    report_lines = [
        "# RetailIQ Validation Report",
        "",
        "## Executive Summary",
        "",
        f"- Pipeline status: **{pipeline_status}**",
        f"- Validation score: **{validation_score}/100**",
        f"- Checks passed: **{passed_count}**",
        f"- Checks failed: **{failed_count}**",
        "",
        "> The validation score is based on documented rule-based "
        "checks and should be reviewed alongside the detailed results.",
        "",
        "## Validation Summary",
        "",
        "| Category | Check | Status | Severity | Result |",
        "|---|---|---|---|---|",
    ]

    for result in results:
        status = "PASS" if result["passed"] else "FAIL"

        report_lines.append(
            f"| {result['category']} | "
            f"{result['check_name']} | "
            f"{status} | "
            f"{result['severity']} | "
            f"{result['message']} |"
        )

    failed_results = [
        result for result in results if not result["passed"]
    ]

    report_lines.extend(
        [
            "",
            "## Failed Checks",
            "",
        ]
    )

    if failed_results:
        for result in failed_results:
            report_lines.append(
                f"- **{result['check_name']}**: "
                f"{result['message']}"
            )
    else:
        report_lines.append(
            "- No failed checks were detected."
        )

    report_lines.extend(
        [
            "",
            "## Recommendation",
            "",
        ]
    )

    if failed_count == 0:
        report_lines.append(
            "The primary raw datasets passed all current validation "
            "checks and may proceed to the cleaning stage."
        )
    else:
        report_lines.append(
            "Resolve failed validation checks before loading the data "
            "into the processed-data layer or SQL warehouse."
        )

    REPORT_PATH.write_text(
        "\n".join(report_lines),
        encoding="utf-8",
    )

    print(f"\nValidation report created:")
    print(REPORT_PATH)


def main() -> None:
    """Run the complete RetailIQ validation workflow."""

    calendar, sales, prices = load_data()

    results = run_validations(
        calendar,
        sales,
        prices,
    )

    print_results(results)
    generate_report(results)


if __name__ == "__main__":
    main()