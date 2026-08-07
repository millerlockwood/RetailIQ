from pathlib import Path
import subprocess
import sys
import time


# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent

ETL_DIR = PROJECT_ROOT / "src" / "etl"


# ==========================================================
# PIPELINE STAGES
# ==========================================================

PIPELINE_STAGES = [
    ("01", "Data Profiling", "01_data_overview.py"),
    ("02", "Data Validation", "02_data_validation.py"),
    ("03", "Data Cleaning", "03_data_cleaning.py"),
    ("04", "Sales Transformation", "04_transform_sales.py"),
    ("05", "Database Build", "05_build_database.py"),
    ("06", "Database Load", "06_load_database.py"),
    ("07", "Index Creation", "07_create_indexes.py"),
    ("08", "View Creation", "08_create_views.py"),
    ("09", "Summary Table Creation", "09_create_summary_tables.py"),
]


# ==========================================================
# RUN ONE STAGE
# ==========================================================

def run_stage(
    stage_number: str,
    stage_name: str,
    script_name: str,
) -> float:
    """Run one RetailIQ pipeline stage."""

    script_path = ETL_DIR / script_name

    if not script_path.exists():
        raise FileNotFoundError(
            f"Pipeline script not found: {script_path}"
        )

    print("\n" + "=" * 70)
    print(
        f"STAGE {stage_number}: {stage_name.upper()}"
    )
    print("=" * 70)

    start_time = time.time()

    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
        ],
        cwd=PROJECT_ROOT,
    )

    elapsed = time.time() - start_time

    if result.returncode != 0:
        print(
            f"\n❌ Stage {stage_number} failed: "
            f"{stage_name}"
        )

        raise RuntimeError(
            "RetailIQ pipeline stopped because "
            "a stage failed."
        )

    print(
        f"\n✅ Stage {stage_number} completed "
        f"in {elapsed:.2f} seconds"
    )

    return elapsed


# ==========================================================
# MAIN PIPELINE
# ==========================================================

def main() -> None:
    """Run the complete RetailIQ pipeline."""

    print("=" * 70)
    print("RETAILIQ END-TO-END DATA PIPELINE")
    print("=" * 70)

    print(
        "\nStages scheduled:"
    )

    for number, name, _ in PIPELINE_STAGES:
        print(
            f"  {number}. {name}"
        )

    pipeline_start = time.time()

    stage_times = []

    try:

        for (
            stage_number,
            stage_name,
            script_name,
        ) in PIPELINE_STAGES:

            elapsed = run_stage(
                stage_number,
                stage_name,
                script_name,
            )

            stage_times.append(
                (
                    stage_number,
                    stage_name,
                    elapsed,
                )
            )

    except Exception as error:

        print("\n" + "=" * 70)
        print("PIPELINE FAILED")
        print("=" * 70)

        print(
            f"\nError: {error}"
        )

        sys.exit(1)

    total_elapsed = (
        time.time() - pipeline_start
    )

    print("\n" + "=" * 70)
    print("RETAILIQ PIPELINE COMPLETE")
    print("=" * 70)

    print("\nStage Summary")
    print("-" * 70)

    for (
        stage_number,
        stage_name,
        elapsed,
    ) in stage_times:

        print(
            f"{stage_number} "
            f"{stage_name:<30} "
            f"{elapsed:>8.2f} sec"
        )

    print("-" * 70)

    print(
        f"\nTotal Runtime: "
        f"{total_elapsed / 60:.2f} minutes"
    )

    print(
        "\n✅ RetailIQ is ready for analytics."
    )


if __name__ == "__main__":
    main()