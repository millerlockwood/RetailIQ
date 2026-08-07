from pathlib import Path

import joblib
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

MODEL_PATH = (
    PROJECT_ROOT
    / "data"
    / "forecasting"
    / "random_forest_model.joblib"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "forecasting"
)

REPORT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "forecasting"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "next_week_store_forecast.parquet"
)

CSV_OUTPUT_PATH = (
    REPORT_DIR
    / "next_week_store_forecast.csv"
)


# ==========================================================
# MAIN
# ==========================================================

def main() -> None:
    """
    Generate next-week demand forecasts for each store.
    """

    print("=" * 60)
    print("RETAILIQ NEXT-WEEK DEMAND FORECAST")
    print("=" * 60)

    # ------------------------------------------------------
    # LOAD HISTORICAL DATA
    # ------------------------------------------------------

    dataframe = pd.read_parquet(
        INPUT_PATH
    )

    dataframe["week_start_date"] = pd.to_datetime(
        dataframe["week_start_date"]
    )

    dataframe = dataframe.sort_values(
        [
            "store_id",
            "week_start_date",
        ]
    ).reset_index(drop=True)

    print(
        f"\nHistorical rows: "
        f"{len(dataframe):,}"
    )

    # ------------------------------------------------------
    # REMOVE INCOMPLETE FINAL WEEK
    # ------------------------------------------------------

    weekly_totals = (
        dataframe
        .groupby("week_start_date")[
            "weekly_units_sold"
        ]
        .sum()
        .sort_index()
    )

    last_date = weekly_totals.index.max()

    previous_weeks = weekly_totals.iloc[-9:-1]

    typical_recent_demand = (
        previous_weeks.median()
    )

    final_week_demand = (
        weekly_totals.loc[last_date]
    )

    if (
        final_week_demand
        < typical_recent_demand * 0.75
    ):

        print(
            f"\nIncomplete final week detected: "
            f"{last_date.date()}"
        )

        print(
            f"Final week demand: "
            f"{final_week_demand:,.0f}"
        )

        print(
            f"Recent weekly median: "
            f"{typical_recent_demand:,.0f}"
        )

        dataframe = dataframe[
            dataframe["week_start_date"]
            < last_date
        ].copy()

    # ------------------------------------------------------
    # LOAD TRAINED MODEL
    # ------------------------------------------------------

    model_package = joblib.load(
        MODEL_PATH
    )

    model = model_package[
        "model"
    ]

    trained_feature_columns = (
        model_package[
            "feature_columns"
        ]
    )

    # ------------------------------------------------------
    # DETERMINE NEXT FORECAST WEEK
    # ------------------------------------------------------

    latest_week = (
        dataframe["week_start_date"]
        .max()
    )

    forecast_date = (
        latest_week
        + pd.Timedelta(days=7)
    )

    print(
        f"\nLatest complete week: "
        f"{latest_week.date()}"
    )

    print(
        f"Forecast week: "
        f"{forecast_date.date()}"
    )

    # ------------------------------------------------------
    # CREATE ONE FUTURE ROW PER STORE
    # ------------------------------------------------------

    future_rows = []

    for store_id, store_data in dataframe.groupby(
        "store_id"
    ):

        store_data = (
            store_data
            .sort_values(
                "week_start_date"
            )
            .reset_index(drop=True)
        )

        if len(store_data) < 52:
            continue

        sales = (
            store_data[
                "weekly_units_sold"
            ]
            .reset_index(drop=True)
        )

        future_rows.append(
            {
                "store_id": store_id,

                "week_start_date":
                    forecast_date,

                "month":
                    forecast_date.month,

                "week_of_year":
                    int(
                        forecast_date
                        .isocalendar()
                        .week
                    ),

                "quarter":
                    forecast_date.quarter,

                "year":
                    forecast_date.year,

                "lag_1":
                    sales.iloc[-1],

                "lag_2":
                    sales.iloc[-2],

                "lag_4":
                    sales.iloc[-4],

                "lag_13":
                    sales.iloc[-13],

                "lag_52":
                    sales.iloc[-52],

                "rolling_4_week_avg":
                    sales.iloc[-4:].mean(),

                "rolling_13_week_avg":
                    sales.iloc[-13:].mean(),

                "rolling_26_week_avg":
                    sales.iloc[-26:].mean(),
            }
        )

    future = pd.DataFrame(
        future_rows
    )

    # ------------------------------------------------------
    # PREPARE MODEL FEATURES
    # ------------------------------------------------------

    model_features = future[
        [
            "store_id",
            "month",
            "week_of_year",
            "quarter",
            "year",
            "lag_1",
            "lag_2",
            "lag_4",
            "lag_13",
            "lag_52",
            "rolling_4_week_avg",
            "rolling_13_week_avg",
            "rolling_26_week_avg",
        ]
    ].copy()

    model_features = pd.get_dummies(
        model_features,
        columns=["store_id"],
        dtype=int,
    )

    model_features = (
        model_features
        .reindex(
            columns=trained_feature_columns,
            fill_value=0,
        )
    )

    # ------------------------------------------------------
    # GENERATE FORECAST
    # ------------------------------------------------------

    future["forecast_units"] = (
        model.predict(
            model_features
        )
    )

    future["forecast_units"] = (
        future["forecast_units"]
        .round()
        .astype(int)
    )

    # Seasonal baseline for comparison
    future["seasonal_baseline"] = (
        future["lag_52"]
        .round()
        .astype(int)
    )

    # ------------------------------------------------------
    # FINAL OUTPUT
    # ------------------------------------------------------

    results = future[
        [
            "store_id",
            "week_start_date",
            "forecast_units",
            "seasonal_baseline",
            "lag_1",
            "rolling_4_week_avg",
        ]
    ].copy()

    results = results.sort_values(
        "forecast_units",
        ascending=False,
    ).reset_index(drop=True)

    # ------------------------------------------------------
    # SAVE
    # ------------------------------------------------------

    results.to_parquet(
        OUTPUT_PATH,
        index=False,
    )

    results.to_csv(
        CSV_OUTPUT_PATH,
        index=False,
    )

    # ------------------------------------------------------
    # PRINT RESULTS
    # ------------------------------------------------------

    print("\n" + "=" * 60)
    print("NEXT-WEEK STORE FORECAST")
    print("=" * 60)

    print(
        results[
            [
                "store_id",
                "forecast_units",
            ]
        ].to_string(
            index=False
        )
    )

    print(
        "\nTotal predicted demand: "
        f"{results['forecast_units'].sum():,} units"
    )

    print(
        f"\nParquet saved -> "
        f"{OUTPUT_PATH}"
    )

    print(
        f"CSV saved -> "
        f"{CSV_OUTPUT_PATH}"
    )

    print(
        "\nFuture demand forecast complete."
    )


if __name__ == "__main__":
    main()