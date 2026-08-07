from pathlib import Path

import numpy as np
import pandas as pd


# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

HISTORICAL_PATH = (
    PROJECT_ROOT
    / "data"
    / "forecasting"
    / "weekly_store_sales.parquet"
)

FORECAST_PATH = (
    PROJECT_ROOT
    / "reports"
    / "forecasting"
    / "next_week_store_forecast.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "inventory"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "optimized_inventory_recommendations.csv"
)


# ==========================================================
# SETTINGS
# ==========================================================

# Approximately 95% service level
SERVICE_LEVEL_Z = 1.645

# Number of recent weeks used to estimate demand variability
VARIABILITY_WINDOW = 26


# ==========================================================
# MAIN
# ==========================================================

def main() -> None:
    """
    Generate data-driven inventory recommendations using
    forecast demand and historical demand variability.
    """

    print("=" * 60)
    print("RETAILIQ OPTIMIZED INVENTORY MODEL")
    print("=" * 60)

    # ------------------------------------------------------
    # LOAD DATA
    # ------------------------------------------------------

    historical = pd.read_parquet(
        HISTORICAL_PATH
    )

    forecast = pd.read_csv(
        FORECAST_PATH
    )

    historical["week_start_date"] = pd.to_datetime(
        historical["week_start_date"]
    )

    forecast["week_start_date"] = pd.to_datetime(
        forecast["week_start_date"]
    )

    # ------------------------------------------------------
    # REMOVE INCOMPLETE FINAL WEEK
    # ------------------------------------------------------

    weekly_totals = (
        historical
        .groupby("week_start_date")["weekly_units_sold"]
        .sum()
        .sort_index()
    )

    last_date = weekly_totals.index.max()

    recent_weeks = weekly_totals.iloc[-9:-1]

    recent_median = recent_weeks.median()

    final_week_demand = weekly_totals.loc[last_date]

    if final_week_demand < recent_median * 0.75:

        historical = historical[
            historical["week_start_date"] < last_date
        ].copy()

        print(
            f"\nExcluded incomplete week: "
            f"{last_date.date()}"
        )

    # ------------------------------------------------------
    # CALCULATE STORE DEMAND VARIABILITY
    # ------------------------------------------------------

    variability_records = []

    for store_id, store_data in historical.groupby(
        "store_id"
    ):

        store_data = store_data.sort_values(
            "week_start_date"
        )

        recent_store_data = store_data.tail(
            VARIABILITY_WINDOW
        )

        demand_std = (
            recent_store_data[
                "weekly_units_sold"
            ].std()
        )

        average_demand = (
            recent_store_data[
                "weekly_units_sold"
            ].mean()
        )

        variability_records.append(
            {
                "store_id": store_id,
                "average_recent_demand":
                    average_demand,
                "demand_std":
                    demand_std,
            }
        )

    variability = pd.DataFrame(
        variability_records
    )

    # ------------------------------------------------------
    # COMBINE WITH FORECAST
    # ------------------------------------------------------

    results = forecast.merge(
        variability,
        on="store_id",
        how="left",
    )

    # ------------------------------------------------------
    # DATA-DRIVEN SAFETY STOCK
    # ------------------------------------------------------

    results["optimized_safety_stock"] = (
        SERVICE_LEVEL_Z
        * results["demand_std"]
    ).round().astype(int)

    # ------------------------------------------------------
    # RECOMMENDED INVENTORY
    # ------------------------------------------------------

    results["recommended_inventory"] = (
        results["forecast_units"]
        + results["optimized_safety_stock"]
    )

    # ------------------------------------------------------
    # COMPARE AGAINST 15% POLICY
    # ------------------------------------------------------

    results["flat_15pct_safety_stock"] = (
        results["forecast_units"]
        * 0.15
    ).round().astype(int)

    results["flat_15pct_inventory"] = (
        results["forecast_units"]
        + results["flat_15pct_safety_stock"]
    )

    results["inventory_difference"] = (
        results["recommended_inventory"]
        - results["flat_15pct_inventory"]
    )

    # ------------------------------------------------------
    # VARIABILITY MEASURE
    # ------------------------------------------------------

    results["coefficient_of_variation"] = (
        results["demand_std"]
        / results["average_recent_demand"]
    )

    # ------------------------------------------------------
    # RISK CLASSIFICATION
    # ------------------------------------------------------

    conditions = [
        results["coefficient_of_variation"] < 0.10,
        results["coefficient_of_variation"] < 0.20,
    ]

    choices = [
        "Low",
        "Medium",
    ]

    results["demand_variability"] = np.select(
        conditions,
        choices,
        default="High",
    )

    # ------------------------------------------------------
    # FINAL OUTPUT
    # ------------------------------------------------------

    final_columns = [
        "store_id",
        "week_start_date",
        "forecast_units",
        "average_recent_demand",
        "demand_std",
        "coefficient_of_variation",
        "demand_variability",
        "optimized_safety_stock",
        "recommended_inventory",
        "flat_15pct_inventory",
        "inventory_difference",
    ]

    results = results[
        final_columns
    ].copy()

    results = results.sort_values(
        "recommended_inventory",
        ascending=False,
    ).reset_index(drop=True)

    # ------------------------------------------------------
    # SAVE
    # ------------------------------------------------------

    results.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    # ------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------

    optimized_total = (
        results[
            "recommended_inventory"
        ].sum()
    )

    flat_total = (
        results[
            "flat_15pct_inventory"
        ].sum()
    )

    difference = (
        optimized_total
        - flat_total
    )

    print("\n" + "=" * 60)
    print("OPTIMIZED INVENTORY PLAN")
    print("=" * 60)

    display_columns = [
        "store_id",
        "forecast_units",
        "optimized_safety_stock",
        "recommended_inventory",
        "demand_variability",
    ]

    print(
        results[
            display_columns
        ].to_string(
            index=False
        )
    )

    print(
        f"\nService Level Target: "
        f"95%"
    )

    print(
        f"Variability Window: "
        f"{VARIABILITY_WINDOW} weeks"
    )

    print(
        f"\nForecast Demand: "
        f"{results['forecast_units'].sum():,} units"
    )

    print(
        f"Optimized Inventory: "
        f"{optimized_total:,} units"
    )

    print(
        f"Flat 15% Inventory: "
        f"{flat_total:,} units"
    )

    print(
        f"Difference vs 15% Policy: "
        f"{difference:+,} units"
    )

    print(
        f"\nSaved -> "
        f"{OUTPUT_PATH}"
    )

    print(
        "\nOptimized inventory model complete."
    )


if __name__ == "__main__":
    main()