from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "forecasting"
    / "demand_model_predictions.parquet"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "forecasting"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "actual_vs_forecast.png"
)


# ==========================================================
# MAIN
# ==========================================================

def main() -> None:
    """Create an actual-vs-forecast visualization."""

    print("=" * 60)
    print("RETAILIQ FORECAST VISUALIZATION")
    print("=" * 60)

    dataframe = pd.read_parquet(
        INPUT_PATH
    )

    dataframe["week_start_date"] = pd.to_datetime(
        dataframe["week_start_date"]
    )

    # ------------------------------------------------------
    # Aggregate across all stores by week
    # ------------------------------------------------------

    weekly = (
        dataframe
        .groupby("week_start_date", as_index=False)
        .agg(
            actual_units=(
                "weekly_units_sold",
                "sum",
            ),
            baseline_forecast=(
                "baseline_forecast",
                "sum",
            ),
            model_forecast=(
                "model_forecast",
                "sum",
            ),
        )
        .sort_values("week_start_date")
    )

    # ------------------------------------------------------
    # Create Chart
    # ------------------------------------------------------

    plt.figure(
        figsize=(12, 6)
    )

    plt.plot(
        weekly["week_start_date"],
        weekly["actual_units"],
        label="Actual Demand",
        linewidth=2,
    )

    plt.plot(
        weekly["week_start_date"],
        weekly["model_forecast"],
        label="Random Forest Forecast",
        linewidth=2,
    )

    plt.plot(
        weekly["week_start_date"],
        weekly["baseline_forecast"],
        label="Seasonal Baseline",
        linewidth=1.5,
        alpha=0.7,
    )

    plt.title(
        "RetailIQ Weekly Demand Forecast Performance",
        fontsize=14,
        fontweight="bold",
    )

    plt.xlabel(
        "Week"
    )

    plt.ylabel(
        "Units Sold"
    )

    plt.legend()

    plt.grid(
        alpha=0.25
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_PATH,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()

    print(
        f"\nSaved -> {OUTPUT_PATH}"
    )

    print(
        "\nForecast visualization complete."
    )


if __name__ == "__main__":
    main()