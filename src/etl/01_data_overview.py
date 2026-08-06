from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORT_PATH = REPORTS_DIR / "Data_Quality_Report.md"


def load_datasets() -> dict[str, pd.DataFrame]:
    """Load the main RetailIQ datasets from the raw data folder."""
    return {
        "Calendar": pd.read_csv(RAW_DATA_DIR / "calendar.csv"),
        "Sales Validation": pd.read_csv(
            RAW_DATA_DIR / "sales_train_validation.csv"
        ),
        "Sell Prices": pd.read_csv(RAW_DATA_DIR / "sell_prices.csv"),
    }


def create_dataset_profile(
    name: str,
    dataframe: pd.DataFrame,
) -> str:
    """Create a Markdown profile for one dataset."""
    row_count, column_count = dataframe.shape
    duplicate_count = int(dataframe.duplicated().sum())
    memory_mb = dataframe.memory_usage(deep=True).sum() / 1024**2

    profile_lines = [
        f"## {name}",
        "",
        "### Dataset Summary",
        "",
        f"- Rows: {row_count:,}",
        f"- Columns: {column_count:,}",
        f"- Duplicate rows: {duplicate_count:,}",
        f"- Memory usage: {memory_mb:,.2f} MB",
        "",
        "### Column Profile",
        "",
        "| Column | Data Type | Missing Values | Missing % | Unique Values |",
        "|---|---:|---:|---:|---:|",
    ]

    for column in dataframe.columns:
        missing_count = int(dataframe[column].isna().sum())
        missing_percentage = (
            missing_count / row_count * 100 if row_count else 0
        )
        unique_count = int(dataframe[column].nunique(dropna=True))

        profile_lines.append(
            f"| {column} | {dataframe[column].dtype} | "
            f"{missing_count:,} | {missing_percentage:.2f}% | "
            f"{unique_count:,} |"
        )

    profile_lines.extend(
        [
            "",
            "### First Five Rows",
            "",
            dataframe.head().to_markdown(index=False),
            "",
            "---",
            "",
        ]
    )

    return "\n".join(profile_lines)


def generate_report(datasets: dict[str, pd.DataFrame]) -> None:
    """Generate and save the complete Markdown profiling report."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    report_sections = [
        "# RetailIQ Data Quality Report",
        "",
        "This report summarizes the structure, completeness, uniqueness, "
        "and memory usage of the primary raw datasets.",
        "",
    ]

    for dataset_name, dataframe in datasets.items():
        print(f"Profiling {dataset_name}...")
        report_sections.append(
            create_dataset_profile(dataset_name, dataframe)
        )

    REPORT_PATH.write_text(
        "\n".join(report_sections),
        encoding="utf-8",
    )

    print(f"\nReport created successfully:")
    print(REPORT_PATH)


def main() -> None:
    """Run the RetailIQ data profiling workflow."""
    datasets = load_datasets()
    generate_report(datasets)


if __name__ == "__main__":
    main()