from pathlib import Path

import pandas as pd


# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

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
    / "inventory_recommendations.csv"
)


# ==========================================================
# SETTINGS
# ==========================================================

# Safety stock percentage used to protect against
# forecast uncertainty and unexpected demand spikes.
SAFETY_STOCK_PERCENT = 0.15


# ==========================================================
# MAIN
# ==========================================================

def main() -> None:
    """
    Generate store-level inventory recommendations
    from next-week demand forecasts.
    """

    print("=" * 60)
    print("RETAILIQ INVENTORY RECOMMENDATIONS")
    print("=" * 60)

    # ------------------------------------------------------
    # LOAD FORECAST
    # ------------------------------------------------------

    dataframe = pd.read_csv(
        FORECAST_PATH
    )

    dataframe["week_start_date"] = pd.to_datetime(
        dataframe["week_start_date"]
    )

    # ------------------------------------------------------
    # SAFETY STOCK
    # ------------------------------------------------------

    dataframe["safety_stock_units"] = (
        dataframe["forecast_units"]
        * SAFETY_STOCK_PERCENT
    ).round().astype(int)

    # ------------------------------------------------------
    # RECOMMENDED INVENTORY
    # ------------------------------------------------------

    dataframe["recommended_inventory_units"] = (
        dataframe["forecast_units"]
        + dataframe["safety_stock_units"]
    )

    # ------------------------------------------------------
    # DEMAND RISK
    # ------------------------------------------------------

    dataframe["demand_risk"] = pd.cut(
        dataframe["forecast_units"],
        bins=[
            -1,
            25000,
            35000,
            float("inf"),
        ],
        labels=[
            "Low",
            "Medium",
            "High",
        ],
    )

    # ------------------------------------------------------
    # FINAL OUTPUT
    # ------------------------------------------------------

    results = dataframe[
        [
            "store_id",
            "week_start_date",
            "forecast_units",
            "safety_stock_units",
            "recommended_inventory_units",
            "demand_risk",
        ]
    ].copy()

    results = results.sort_values(
        "recommended_inventory_units",
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
    # PRINT RESULTS
    # ------------------------------------------------------

    print("\n" + "=" * 60)
    print("STORE INVENTORY PLAN")
    print("=" * 60)

    print(
        results.to_string(
            index=False
        )
    )

    print(
        "\nTotal Forecast Demand: "
        f"{results['forecast_units'].sum():,} units"
    )

    print(
        "Total Safety Stock: "
        f"{results['safety_stock_units'].sum():,} units"
    )

    print(
        "Total Recommended Inventory: "
        f"{results['recommended_inventory_units'].sum():,} units"
    )

    print(
        f"\nSafety Stock Policy: "
        f"{SAFETY_STOCK_PERCENT:.0%}"
    )

    print(
        f"\nSaved -> {OUTPUT_PATH}"
    )

    print(
        "\nInventory recommendation workflow complete."
    )


if __name__ == "__main__":
    main()