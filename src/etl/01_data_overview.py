from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORT_PATH = REPORTS_DIR / "01_Data_Quality_Report.md"


DATASET_FILES = {
    "Calendar": "calendar.csv",
    "Sales Validation": "sales_train_validation.csv",
    "Sell Prices": "sell_prices.csv",
}


EXPECTED_NULL_COLUMNS = {
    "Calendar": {
        "event_name_1",
        "event_type_1",
        "event_name_2",
        "event_type_2",
    }
}


RECOMMENDED_DATA_TYPES = {
    "Calendar": {
        "date": "datetime",
        "weekday": "category",
        "event_name_1": "category",
        "event_type_1": "category",
        "event_name_2": "category",
        "event_type_2": "category",
    },
    "Sales Validation": {
        "item_id": "category",
        "dept_id": "category",
        "cat_id": "category",
        "store_id": "category",
        "state_id": "category",
    },
    "Sell Prices": {
        "store_id": "category",
        "item_id": "category",
    },
}


def load_datasets() -> dict[str, pd.DataFrame]:
    """Load the primary RetailIQ datasets."""

    datasets = {}

    for dataset_name, filename in DATASET_FILES.items():
        file_path = RAW_DATA_DIR / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Required dataset was not found: {file_path}"
            )

        datasets[dataset_name] = pd.read_csv(file_path)

    return datasets


def evaluate_dataset(
    name: str,
    dataframe: pd.DataFrame,
) -> tuple[int, list[str], list[str], list[str]]:
    """
    Evaluate one dataset using transparent data-quality rules.

    Returns:
        score
        findings
        warnings
        recommendations
    """

    score = 100
    findings = []
    warnings = []
    recommendations = []

    row_count = len(dataframe)
    duplicate_count = int(dataframe.duplicated().sum())

    expected_nulls = EXPECTED_NULL_COLUMNS.get(name, set())
    recommended_types = RECOMMENDED_DATA_TYPES.get(name, {})

    # Duplicate-row rule
    if duplicate_count == 0:
        findings.append("No fully duplicated rows were detected.")
    else:
        score -= 15
        warnings.append(
            f"{duplicate_count:,} fully duplicated rows were detected."
        )
        recommendations.append(
            "Investigate duplicated rows before loading this dataset into SQL."
        )

    # Missing-value rules
    unexpected_missing_columns = []

    for column in dataframe.columns:
        missing_count = int(dataframe[column].isna().sum())

        if missing_count == 0:
            continue

        missing_percentage = (
            missing_count / row_count * 100 if row_count else 0
        )

        if column in expected_nulls:
            findings.append(
                f"`{column}` is {missing_percentage:.2f}% null. "
                "This is expected because most calendar dates do not "
                "contain a special event."
            )
        else:
            unexpected_missing_columns.append(
                (column, missing_count, missing_percentage)
            )

    if unexpected_missing_columns:
        score -= min(30, len(unexpected_missing_columns) * 5)

        for column, missing_count, missing_percentage in (
            unexpected_missing_columns
        ):
            warnings.append(
                f"`{column}` contains {missing_count:,} missing values "
                f"({missing_percentage:.2f}%)."
            )

        recommendations.append(
            "Investigate unexpected missing values and define a documented "
            "treatment rule before modeling."
        )
    else:
        findings.append(
            "No unexpected missing-value issues were identified."
        )

    # Empty-dataset rule
    if row_count == 0:
        score = 0
        warnings.append("The dataset contains no rows.")
        recommendations.append(
            "Verify the source file and extraction process."
        )

    # Data-type recommendations
    for column, recommended_type in recommended_types.items():
        if column not in dataframe.columns:
            continue

        current_type = str(dataframe[column].dtype)

        if recommended_type == "datetime" and not pd.api.types.is_datetime64_any_dtype(
            dataframe[column]
        ):
            recommendations.append(
                f"Convert `{column}` from `{current_type}` to datetime."
            )

        if recommended_type == "category" and current_type != "category":
            recommendations.append(
                f"Consider converting `{column}` from `{current_type}` "
                "to category to reduce memory usage."
            )

    score = max(0, min(100, score))

    return score, findings, warnings, recommendations


def score_label(score: int) -> str:
    """Convert a numeric score into a readable quality label."""

    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Good"
    if score >= 60:
        return "Needs Review"

    return "High Risk"


def format_bullet_section(
    heading: str,
    items: list[str],
    empty_message: str,
) -> list[str]:
    """Create a Markdown bullet-list section."""

    lines = [f"### {heading}", ""]

    if items:
        lines.extend(f"- {item}" for item in items)
    else:
        lines.append(f"- {empty_message}")

    lines.append("")

    return lines


def create_dataset_profile(
    name: str,
    dataframe: pd.DataFrame,
) -> str:
    """Create a complete Markdown profile for one dataset."""

    row_count, column_count = dataframe.shape
    duplicate_count = int(dataframe.duplicated().sum())
    memory_mb = dataframe.memory_usage(deep=True).sum() / 1024**2

    score, findings, warnings, recommendations = evaluate_dataset(
        name,
        dataframe,
    )

    profile_lines = [
        f"## {name}",
        "",
        "### Dataset Health",
        "",
        f"- Quality score: **{score}/100**",
        f"- Status: **{score_label(score)}**",
        "",
        "### Dataset Summary",
        "",
        f"- Rows: {row_count:,}",
        f"- Columns: {column_count:,}",
        f"- Duplicate rows: {duplicate_count:,}",
        f"- Memory usage: {memory_mb:,.2f} MB",
        "",
    ]

    profile_lines.extend(
        format_bullet_section(
            "Key Findings",
            findings,
            "No notable findings were generated.",
        )
    )

    profile_lines.extend(
        format_bullet_section(
            "Potential Issues",
            warnings,
            "No major data-quality warnings were detected.",
        )
    )

    profile_lines.extend(
        format_bullet_section(
            "Recommended Actions",
            recommendations,
            "No immediate corrective action is required.",
        )
    )

    profile_lines.extend(
        [
            "### Column Profile",
            "",
            "| Column | Data Type | Missing Values | Missing % | "
            "Unique Values |",
            "|---|---:|---:|---:|---:|",
        ]
    )

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


def create_executive_summary(
    dataset_results: dict[str, tuple[int, list[str], list[str], list[str]]],
) -> str:
    """Create a high-level quality summary across all datasets."""

    lines = [
        "## Executive Summary",
        "",
        "| Dataset | Quality Score | Status | Warning Count |",
        "|---|---:|---|---:|",
    ]

    for dataset_name, result in dataset_results.items():
        score, _, warnings, _ = result

        lines.append(
            f"| {dataset_name} | {score}/100 | "
            f"{score_label(score)} | {len(warnings)} |"
        )

    lines.extend(
        [
            "",
            "> Scores are generated using documented, rule-based checks. "
            "They are screening indicators and do not replace analyst review.",
            "",
        ]
    )

    return "\n".join(lines)


def generate_report(datasets: dict[str, pd.DataFrame]) -> None:
    """Generate and save the complete Markdown report."""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    dataset_results = {
        name: evaluate_dataset(name, dataframe)
        for name, dataframe in datasets.items()
    }

    report_sections = [
        "# RetailIQ Data Quality Report",
        "",
        "This automated report evaluates the structure, completeness, "
        "uniqueness, memory usage, and potential preparation needs of "
        "the primary raw datasets.",
        "",
        create_executive_summary(dataset_results),
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

    print("\nReport created successfully:")
    print(REPORT_PATH)


def main() -> None:
    """Run the RetailIQ data-profiling workflow."""

    try:
        datasets = load_datasets()
        generate_report(datasets)
    except (FileNotFoundError, pd.errors.ParserError) as error:
        print(f"Data profiling failed: {error}")
        raise


if __name__ == "__main__":
    main()