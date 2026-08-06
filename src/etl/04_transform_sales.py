from pathlib import Path
import re

import pandas as pd


# ============================================
# PATHS
# ============================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"

REPORT_PATH = REPORTS_DIR / "04_Transformation_Report.md"


# ============================================
# LOAD DATA
# ============================================

def load_sales() -> pd.DataFrame:
    """Load the raw evaluation sales dataset."""

    return pd.read_csv(
        RAW_DATA_DIR / "sales_train_evaluation.csv",
        low_memory=False,
    )


def load_calendar() -> pd.DataFrame:
    """Load the calendar mapping for day IDs and real dates."""

    calendar = pd.read_csv(
        RAW_DATA_DIR / "calendar.csv",
        usecols=["d", "date", "wm_yr_wk"],
    )

    calendar["date"] = pd.to_datetime(
        calendar["date"],
        errors="raise",
    )

    return calendar


# ============================================
# IDENTIFY SALES COLUMNS
# ============================================

def identify_sales_columns(
    sales: pd.DataFrame,
) -> tuple[list[str], list[str]]:
    """Identify identifier columns and daily sales columns."""

    id_columns = [
        "id",
        "item_id",
        "dept_id",
        "cat_id",
        "store_id",
        "state_id",
    ]

    day_columns = [
        column
        for column in sales.columns
        if re.fullmatch(r"d_\d+", column)
    ]

    missing_id_columns = [
        column
        for column in id_columns
        if column not in sales.columns
    ]

    if missing_id_columns:
        raise ValueError(
            f"Missing required ID columns: {missing_id_columns}"
        )

    if not day_columns:
        raise ValueError(
            "No daily sales columns were detected."
        )

    return id_columns, day_columns


# ============================================
# WIDE-TO-LONG TRANSFORMATION
# ============================================

def transform_sales(
    sales: pd.DataFrame,
    id_columns: list[str],
    day_columns: list[str],
) -> pd.DataFrame:
    """Convert wide daily sales columns into long format."""

    return sales.melt(
        id_vars=id_columns,
        value_vars=day_columns,
        var_name="d",
        value_name="sales",
    )


# ============================================
# ATTACH CALENDAR INFORMATION
# ============================================

def attach_calendar(
    sales_long: pd.DataFrame,
    calendar: pd.DataFrame,
) -> pd.DataFrame:
    """Attach actual dates and retail week identifiers."""

    merged = sales_long.merge(
        calendar,
        on="d",
        how="left",
        validate="many_to_one",
    )

    missing_dates = int(
        merged["date"].isna().sum()
    )

    if missing_dates > 0:
        raise ValueError(
            f"{missing_dates:,} sales rows could not be matched "
            "to a calendar date."
        )

    return merged


# ============================================
# MEMORY OPTIMIZATION
# ============================================

def optimize_transformed_sales(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Reduce memory usage of the transformed sales dataset."""

    category_columns = [
        "id",
        "item_id",
        "dept_id",
        "cat_id",
        "store_id",
        "state_id",
        "d",
    ]

    for column in category_columns:
        dataframe[column] = (
            dataframe[column]
            .astype("category")
        )

    dataframe["sales"] = pd.to_numeric(
        dataframe["sales"],
        downcast="unsigned",
    )

    dataframe["wm_yr_wk"] = pd.to_numeric(
        dataframe["wm_yr_wk"],
        downcast="unsigned",
    )

    return dataframe


# ============================================
# VALIDATION
# ============================================

def validate_transformation(
    sales: pd.DataFrame,
    transformed: pd.DataFrame,
    day_columns: list[str],
) -> list[str]:
    """Validate the wide-to-long transformation."""

    checks = []

    expected_rows = (
        len(sales)
        * len(day_columns)
    )

    actual_rows = len(transformed)

    if expected_rows != actual_rows:
        raise ValueError(
            "Transformed row count does not match "
            "the expected row count."
        )

    checks.append(
        f"Expected row count matched: {actual_rows:,} rows."
    )

    missing_dates = int(
        transformed["date"].isna().sum()
    )

    if missing_dates != 0:
        raise ValueError(
            f"{missing_dates:,} transformed rows are missing dates."
        )

    checks.append(
        "All transformed sales rows matched a valid calendar date."
    )

    missing_sales = int(
        transformed["sales"].isna().sum()
    )

    if missing_sales != 0:
        raise ValueError(
            f"{missing_sales:,} transformed rows contain missing sales."
        )

    checks.append(
        "No missing sales values were detected."
    )

    return checks


# ============================================
# SAVE DATA
# ============================================

def save_transformed_data(
    sales_long: pd.DataFrame,
) -> Path:
    """Save transformed sales data as compressed Parquet."""

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        PROCESSED_DATA_DIR
        / "daily_sales_long.parquet"
    )

    sales_long.to_parquet(
        output_path,
        index=False,
        compression="snappy",
    )

    return output_path


# ============================================
# REPORTING
# ============================================

def generate_transformation_report(
    original_shape: tuple[int, int],
    final_dataframe: pd.DataFrame,
    day_columns: list[str],
    validation_checks: list[str],
    output_path: Path,
) -> None:
    """Generate the RetailIQ transformation report."""

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_lines = [
        "# RetailIQ Transformation Report",
        "",
        "## Executive Summary",
        "",
        "- Transformation status: **COMPLETED**",
        (
            f"- Original shape: **{original_shape[0]:,} rows × "
            f"{original_shape[1]:,} columns**"
        ),
        f"- Final rows: **{len(final_dataframe):,}**",
        f"- Daily columns transformed: **{len(day_columns):,}**",
        f"- Day range: **{day_columns[0]} → {day_columns[-1]}**",
        "- Calendar relationship: **VALIDATED**",
        "",
        "## Transformation Performed",
        "",
        (
            "The raw M5 sales dataset was converted from a wide "
            "time-series structure into an analytics-ready long format."
        ),
        "",
        "### Before",
        "",
        "`item_id | store_id | d_1 | d_2 | ... | d_1941`",
        "",
        "### After",
        "",
        "`date | item_id | store_id | sales | wm_yr_wk`",
        "",
        "## Validation Checks",
        "",
    ]

    for check in validation_checks:
        report_lines.append(
            f"- {check}"
        )

    report_lines.extend(
        [
            "",
            "## Output Dataset",
            "",
            f"- Rows: **{len(final_dataframe):,}**",
            f"- Columns: **{final_dataframe.shape[1]}**",
            f"- Output file: `{output_path}`",
            "",
            "## Business Purpose",
            "",
            (
                "The transformed dataset creates one record for each "
                "store-item-date combination, making the data suitable "
                "for SQL analysis, Power BI reporting, forecasting, "
                "and inventory optimization."
            ),
            "",
            "## Recommendation",
            "",
            (
                "The transformed daily sales dataset is ready for "
                "loading into the RetailIQ SQL warehouse."
            ),
        ]
    )

    REPORT_PATH.write_text(
        "\n".join(report_lines),
        encoding="utf-8",
    )


# ============================================
# MAIN WORKFLOW
# ============================================

def main() -> None:
    """Run the complete RetailIQ sales transformation workflow."""

    print("=" * 60)
    print("RETAILIQ SALES TRANSFORMATION")
    print("=" * 60)

    print("\nLoading source data...")

    sales = load_sales()
    calendar = load_calendar()

    original_shape = sales.shape

    print(
        f"Original Sales Shape: {original_shape}"
    )

    id_columns, day_columns = identify_sales_columns(
        sales
    )

    print(
        f"\nID Columns: {len(id_columns)}"
    )

    print(
        f"Daily Columns: {len(day_columns)}"
    )

    print(
        f"Day Range: {day_columns[0]} -> {day_columns[-1]}"
    )

    print(
        "\nTransforming sales from wide to long format..."
    )

    sales_long = transform_sales(
        sales,
        id_columns,
        day_columns,
    )

    print(
        f"Long-format shape: {sales_long.shape}"
    )

    print(
        "\nAttaching calendar dates..."
    )

    sales_long = attach_calendar(
        sales_long,
        calendar,
    )

    print(
        "Calendar relationship validated."
    )

    print(
        "\nOptimizing transformed data..."
    )

    sales_long = optimize_transformed_sales(
        sales_long
    )

    print(
        "\nValidating transformation..."
    )

    validation_checks = validate_transformation(
        sales,
        sales_long,
        day_columns,
    )

    for check in validation_checks:
        print(
            f"✅ {check}"
        )

    print(
        "\nFinal Columns:"
    )

    print(
        sales_long.columns.tolist()
    )

    print(
        "\nFirst Five Rows:"
    )

    print(
        sales_long[
            [
                "date",
                "item_id",
                "store_id",
                "sales",
                "wm_yr_wk",
            ]
        ].head()
    )

    print(
        "\nSaving transformed dataset..."
    )

    output_path = save_transformed_data(
        sales_long
    )

    print(
        "\nGenerating transformation report..."
    )

    generate_transformation_report(
        original_shape=original_shape,
        final_dataframe=sales_long,
        day_columns=day_columns,
        validation_checks=validation_checks,
        output_path=output_path,
    )

    print(
        "\nTRANSFORMATION SUMMARY"
    )

    print(
        "-" * 60
    )

    print(
        f"Rows created: {len(sales_long):,}"
    )

    print(
        f"Columns: {sales_long.shape[1]}"
    )

    print(
        f"Output: {output_path}"
    )

    print(
        f"Report: {REPORT_PATH}"
    )

    print(
        "\nTransformation Complete"
    )


if __name__ == "__main__":
    main()