from pathlib import Path

import pandas as pd


# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "forecasting"
    / "weekly_store_sales.parquet"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "forecasting"
    / "baseline_forecast.parquet"
)


# ==========================================================
# MAIN
# ==========================================================

def main() -> None:
    """Create a seasonal baseline forecast."""

    print("=" * 60)
    print("RETAILIQ BASELINE DEMAND FORECAST")
    print("=" * 60)

    # Load prepared forecasting data
    dataframe = pd.read_parquet(INPUT_PATH)

    dataframe["week_start_date"] = pd.to_datetime(
        dataframe["week_start_date"]
    )

    dataframe = dataframe.sort_values(
        ["store_id", "week_start_date"]
    ).reset_index(drop=True)

    # ------------------------------------------------------
    # BASELINE FORECAST
    # Same store, approximately same week one year earlier
    # ------------------------------------------------------

    dataframe["baseline_forecast"] = (
        dataframe
        .groupby("store_id")["weekly_units_sold"]
        .shift(52)
    )

    # Remove first year because no prior-year forecast exists
    evaluation = dataframe.dropna(
        subset=["baseline_forecast"]
    ).copy()

    # ------------------------------------------------------
    # FORECAST ERROR
    # ------------------------------------------------------

    evaluation["absolute_error"] = (
        evaluation["weekly_units_sold"]
        - evaluation["baseline_forecast"]
    ).abs()

    evaluation["percentage_error"] = (
        evaluation["absolute_error"]
        / evaluation["weekly_units_sold"]
    ) * 100

    mae = evaluation["absolute_error"].mean()
    mape = evaluation["percentage_error"].mean()

    # ------------------------------------------------------
    # RESULTS
    # ------------------------------------------------------

    print(f"\nForecast observations: {len(evaluation):,}")

    print(
        f"Mean Absolute Error (MAE): "
        f"{mae:,.0f} units"
    )

    print(
        f"Mean Absolute Percentage Error (MAPE): "
        f"{mape:.2f}%"
    )

    evaluation.to_parquet(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"\nSaved -> {OUTPUT_PATH}"
    )

    print(
        "\nBaseline forecast complete."
    )


if __name__ == "__main__":
    main()