from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error


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

PREDICTIONS_PATH = (
    OUTPUT_DIR
    / "demand_model_predictions.parquet"
)

MODEL_PATH = (
    OUTPUT_DIR
    / "random_forest_model.joblib"
)

METRICS_PATH = (
    REPORT_DIR
    / "forecast_metrics.csv"
)


# ==========================================================
# SAFE MAPE
# ==========================================================

def calculate_mape(
    actual: pd.Series,
    predicted: pd.Series,
) -> float:
    """
    Calculate MAPE while excluding zero-demand observations.
    """

    mask = actual != 0

    percentage_error = (
        np.abs(
            actual[mask] - predicted[mask]
        )
        / actual[mask]
    )

    return percentage_error.mean() * 100


# ==========================================================
# FEATURE ENGINEERING
# ==========================================================

def create_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create historical demand features for each store.
    """

    dataframe = dataframe.copy()

    dataframe["week_start_date"] = pd.to_datetime(
        dataframe["week_start_date"]
    )

    dataframe = dataframe.sort_values(
        [
            "store_id",
            "week_start_date",
        ]
    ).reset_index(drop=True)

    store_group = dataframe.groupby(
        "store_id"
    )["weekly_units_sold"]

    # -----------------------------------------
    # Lag Features
    # -----------------------------------------

    dataframe["lag_1"] = (
        store_group.shift(1)
    )

    dataframe["lag_2"] = (
        store_group.shift(2)
    )

    dataframe["lag_4"] = (
        store_group.shift(4)
    )

    dataframe["lag_13"] = (
        store_group.shift(13)
    )

    dataframe["lag_52"] = (
        store_group.shift(52)
    )

    # -----------------------------------------
    # Rolling Demand Features
    # -----------------------------------------

    dataframe["rolling_4_week_avg"] = (
        dataframe
        .groupby("store_id")["weekly_units_sold"]
        .transform(
            lambda series:
            series.shift(1).rolling(4).mean()
        )
    )

    dataframe["rolling_13_week_avg"] = (
        dataframe
        .groupby("store_id")["weekly_units_sold"]
        .transform(
            lambda series:
            series.shift(1).rolling(13).mean()
        )
    )

    dataframe["rolling_26_week_avg"] = (
        dataframe
        .groupby("store_id")["weekly_units_sold"]
        .transform(
            lambda series:
            series.shift(1).rolling(26).mean()
        )
    )

    # -----------------------------------------
    # Calendar Features
    # -----------------------------------------

    dataframe["week_of_year"] = (
        dataframe["week_start_date"]
        .dt
        .isocalendar()
        .week
        .astype(int)
    )

    dataframe["quarter"] = (
        dataframe["week_start_date"]
        .dt
        .quarter
    )

    dataframe["year"] = (
        dataframe["week_start_date"]
        .dt
        .year
    )

    # -----------------------------------------
    # Remove rows without enough history
    # -----------------------------------------

    dataframe = dataframe.dropna().copy()

    return dataframe


# ==========================================================
# MAIN
# ==========================================================

def main() -> None:
    """
    Train and evaluate the RetailIQ demand forecasting model.
    """

    print("=" * 60)
    print("RETAILIQ MACHINE LEARNING DEMAND FORECAST")
    print("=" * 60)

    # -----------------------------------------
    # Load Data
    # -----------------------------------------

    dataframe = pd.read_parquet(
        INPUT_PATH
    )

    print(
        f"\nOriginal rows: "
        f"{len(dataframe):,}"
    )

    # -----------------------------------------
    # Feature Engineering
    # -----------------------------------------

    print(
        "\nCreating forecasting features..."
    )

    dataframe = create_features(
        dataframe
    )

    print(
        f"Model-ready rows: "
        f"{len(dataframe):,}"
    )

    # -----------------------------------------
    # Time-Based Train/Test Split
    # -----------------------------------------

    unique_dates = (
        dataframe["week_start_date"]
        .sort_values()
        .unique()
    )

    split_index = int(
        len(unique_dates) * 0.80
    )

    split_date = unique_dates[
        split_index
    ]

    train = dataframe[
        dataframe["week_start_date"]
        < split_date
    ].copy()

    test = dataframe[
        dataframe["week_start_date"]
        >= split_date
    ].copy()

    print(
        f"\nTraining rows: "
        f"{len(train):,}"
    )

    print(
        f"Testing rows: "
        f"{len(test):,}"
    )

    print(
        f"Test starts: "
        f"{pd.Timestamp(split_date).date()}"
    )

    # -----------------------------------------
    # Target
    # -----------------------------------------

    target = "weekly_units_sold"

    # -----------------------------------------
    # Features
    # -----------------------------------------

    feature_columns = [
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

    X_train = train[
        feature_columns
    ].copy()

    X_test = test[
        feature_columns
    ].copy()

    y_train = train[
        target
    ]

    y_test = test[
        target
    ]

    # -----------------------------------------
    # Encode Store ID
    # -----------------------------------------

    X_train = pd.get_dummies(
        X_train,
        columns=["store_id"],
        dtype=int,
    )

    X_test = pd.get_dummies(
        X_test,
        columns=["store_id"],
        dtype=int,
    )

    X_test = X_test.reindex(
        columns=X_train.columns,
        fill_value=0,
    )

    # -----------------------------------------
    # Train Model
    # -----------------------------------------

    print(
        "\nTraining Random Forest model..."
    )

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=None,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train,
    )

    # -----------------------------------------
    # Save Model
    # -----------------------------------------

    joblib.dump(
        {
            "model": model,
            "feature_columns": list(
                X_train.columns
            ),
        },
        MODEL_PATH,
    )

    print(
        f"\nModel saved -> "
        f"{MODEL_PATH}"
    )

    # -----------------------------------------
    # Machine Learning Predictions
    # -----------------------------------------

    predictions = model.predict(
        X_test
    )

    test["model_forecast"] = (
        predictions
    )

    # -----------------------------------------
    # Baseline Forecast
    # -----------------------------------------

    test["baseline_forecast"] = (
        test["lag_52"]
    )

    # -----------------------------------------
    # Model Metrics
    # -----------------------------------------

    model_mae = mean_absolute_error(
        y_test,
        test["model_forecast"],
    )

    model_mape = calculate_mape(
        y_test,
        test["model_forecast"],
    )

    # -----------------------------------------
    # Baseline Metrics
    # -----------------------------------------

    baseline_mae = mean_absolute_error(
        y_test,
        test["baseline_forecast"],
    )

    baseline_mape = calculate_mape(
        y_test,
        test["baseline_forecast"],
    )

    # -----------------------------------------
    # Improvement
    # -----------------------------------------

    mae_improvement = (
        (
            baseline_mae - model_mae
        )
        / baseline_mae
    ) * 100

    # -----------------------------------------
    # Print Results
    # -----------------------------------------

    print("\n" + "=" * 60)
    print("FORECAST RESULTS")
    print("=" * 60)

    print("\nBaseline Model")

    print(
        f"MAE: "
        f"{baseline_mae:,.0f} units"
    )

    print(
        f"MAPE: "
        f"{baseline_mape:.2f}%"
    )

    print("\nRandom Forest Model")

    print(
        f"MAE: "
        f"{model_mae:,.0f} units"
    )

    print(
        f"MAPE: "
        f"{model_mape:.2f}%"
    )

    print(
        f"\nMAE Improvement: "
        f"{mae_improvement:.2f}%"
    )

    # -----------------------------------------
    # Save Predictions
    # -----------------------------------------

    prediction_columns = [
        "store_id",
        "week_start_date",
        "weekly_units_sold",
        "baseline_forecast",
        "model_forecast",
    ]

    test[
        prediction_columns
    ].to_parquet(
        PREDICTIONS_PATH,
        index=False,
    )

    # -----------------------------------------
    # Save Metrics
    # -----------------------------------------

    metrics = pd.DataFrame(
        [
            {
                "Model": "Seasonal Baseline",
                "MAE": round(
                    baseline_mae,
                    2,
                ),
                "MAPE": round(
                    baseline_mape,
                    2,
                ),
            },
            {
                "Model": "Random Forest",
                "MAE": round(
                    model_mae,
                    2,
                ),
                "MAPE": round(
                    model_mape,
                    2,
                ),
            },
        ]
    )

    metrics.to_csv(
        METRICS_PATH,
        index=False,
    )

    print(
        f"\nPredictions saved -> "
        f"{PREDICTIONS_PATH}"
    )

    print(
        f"Metrics saved -> "
        f"{METRICS_PATH}"
    )

    print(
        "\nDemand model complete."
    )


if __name__ == "__main__":
    main()