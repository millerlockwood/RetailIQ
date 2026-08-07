from pathlib import Path
import subprocess
import sys
import time


# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent


# ==========================================================
# PIPELINE STAGES
# ==========================================================

PIPELINE_STAGES = [

    # ------------------------------------------------------
    # DATA ENGINEERING
    # ------------------------------------------------------

    (
        "01",
        "Data Profiling",
        "src/etl/01_data_overview.py",
    ),

    (
        "02",
        "Data Validation",
        "src/etl/02_data_validation.py",
    ),

    (
        "03",
        "Data Cleaning",
        "src/etl/03_data_cleaning.py",
    ),

    (
        "04",
        "Sales Transformation",
        "src/etl/04_transform_sales.py",
    ),

    (
        "05",
        "Database Build",
        "src/etl/05_build_database.py",
    ),

    (
        "06",
        "Database Load",
        "src/etl/06_load_database.py",
    ),

    (
        "07",
        "Index Creation",
        "src/etl/07_create_indexes.py",
    ),

    (
        "08",
        "View Creation",
        "src/etl/08_create_views.py",
    ),

    (
        "09",
        "Summary Table Creation",
        "src/etl/09_create_summary_tables.py",
    ),

    # ------------------------------------------------------
    # BUSINESS ANALYTICS
    # ------------------------------------------------------

    (
        "10",
        "SQL Business Analysis",
        "src/analytics/01_run_sql_analysis.py",
    ),

    (
        "11",
        "Executive KPI Generation",
        "src/analytics/02_generate_kpis.py",
    ),

    (
        "12",
        "Dashboard Data Export",
        "src/analytics/03_dashboard_export.py",
    ),

    # ------------------------------------------------------
    # DEMAND FORECASTING
    # ------------------------------------------------------

    (
        "13",
        "Forecast Data Preparation",
        "src/forecasting/01_prepare_forecasting_data.py",
    ),

    (
        "14",
        "Baseline Forecast",
        "src/forecasting/02_baseline_forecast.py",
    ),

    (
        "15",
        "Machine Learning Demand Model",
        "src/forecasting/03_demand_model.py",
    ),

    (
        "16",
        "Forecast Visualization",
        "src/forecasting/04_forecast_visualization.py",
    ),

    (
        "17",
        "Future Demand Forecast",
        "src/forecasting/05_future_forecast.py",
    ),

    # ------------------------------------------------------
    # INVENTORY OPTIMIZATION
    # ------------------------------------------------------

    (
        "18",
        "Baseline Inventory Policy",
        "src/inventory/01_inventory_recommendations.py",
    ),

    (
        "19",
        "Optimized Inventory Model",
        "src/inventory/02_optimized_inventory.py",
    ),

    (
        "20",
        "Inventory Visualization",
        "src/inventory/03_inventory_visualization.py",
    ),
]


# ==========================================================
# RUN ONE STAGE
# ==========================================================

def run_stage(
    stage_number: str,
    stage_name: str,
    relative_script_path: str,
) -> float:
    """
    Run one RetailIQ pipeline stage.

    The pipeline stops immediately if any stage fails.
    """

    script_path = (
        PROJECT_ROOT
        / relative_script_path
    )

    if not script_path.exists():
        raise FileNotFoundError(
            f"Pipeline script not found: {script_path}"
        )

    print("\n" + "=" * 70)

    print(
        f"STAGE {stage_number}: "
        f"{stage_name.upper()}"
    )

    print("=" * 70)

    print(
        f"Script: {relative_script_path}"
    )

    start_time = time.time()

    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
        ],
        cwd=PROJECT_ROOT,
    )

    elapsed = (
        time.time()
        - start_time
    )

    if result.returncode != 0:

        print(
            f"\n❌ Stage {stage_number} failed: "
            f"{stage_name}"
        )

        raise RuntimeError(
            f"RetailIQ pipeline stopped at "
            f"Stage {stage_number}: {stage_name}"
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
    """
    Run the complete RetailIQ analytics pipeline.
    """

    print("=" * 70)
    print("RETAILIQ END-TO-END ANALYTICS PIPELINE")
    print("=" * 70)

    print(
        "\nPipeline stages:"
    )

    for (
        stage_number,
        stage_name,
        _,
    ) in PIPELINE_STAGES:

        print(
            f"  {stage_number}. "
            f"{stage_name}"
        )

    print(
        f"\nTotal stages: "
        f"{len(PIPELINE_STAGES)}"
    )

    pipeline_start = time.time()

    stage_times = []

    try:

        for (
            stage_number,
            stage_name,
            script_path,
        ) in PIPELINE_STAGES:

            elapsed = run_stage(
                stage_number,
                stage_name,
                script_path,
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

        print(
            "\nAll remaining stages were skipped."
        )

        sys.exit(1)

    total_elapsed = (
        time.time()
        - pipeline_start
    )

    # ------------------------------------------------------
    # FINAL SUMMARY
    # ------------------------------------------------------

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
            f"{stage_number}  "
            f"{stage_name:<35}"
            f"{elapsed:>10.2f} sec"
        )

    print("-" * 70)

    print(
        f"\nTotal Runtime: "
        f"{total_elapsed / 60:.2f} minutes"
    )

    print(
        "\n✅ Data engineering complete."
    )

    print(
        "✅ Analytics outputs generated."
    )

    print(
        "✅ Dashboard datasets generated."
    )

    print(
        "✅ Demand forecasting complete."
    )

    print(
        "✅ Future demand forecast generated."
    )

    print(
        "✅ Inventory recommendations generated."
    )

    print(
        "\nRetailIQ is ready for business decision support."
    )


if __name__ == "__main__":
    main()