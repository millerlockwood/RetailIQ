from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "inventory"
    / "optimized_inventory_recommendations.csv"
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
    / "inventory_policy_comparison.png"
)


# ==========================================================
# MAIN
# ==========================================================

def main() -> None:
    """
    Create a visual comparison of forecast demand,
    flat 15% inventory, and optimized inventory.
    """

    print("=" * 60)
    print("RETAILIQ INVENTORY VISUALIZATION")
    print("=" * 60)

    # ------------------------------------------------------
    # LOAD RESULTS
    # ------------------------------------------------------

    dataframe = pd.read_csv(
        INPUT_PATH
    )

    dataframe = dataframe.sort_values(
        "recommended_inventory",
        ascending=False,
    ).reset_index(drop=True)

    # ------------------------------------------------------
    # CREATE CHART
    # ------------------------------------------------------

    plt.figure(
        figsize=(12, 7)
    )

    x_positions = range(
        len(dataframe)
    )

    bar_width = 0.25

    plt.bar(
        [
            x - bar_width
            for x in x_positions
        ],
        dataframe["forecast_units"],
        width=bar_width,
        label="Forecast Demand",
    )

    plt.bar(
        x_positions,
        dataframe["flat_15pct_inventory"],
        width=bar_width,
        label="Flat 15% Inventory",
    )

    plt.bar(
        [
            x + bar_width
            for x in x_positions
        ],
        dataframe["recommended_inventory"],
        width=bar_width,
        label="Optimized Inventory",
    )

    # ------------------------------------------------------
    # LABELS
    # ------------------------------------------------------

    plt.xticks(
        ticks=list(x_positions),
        labels=dataframe["store_id"],
        rotation=45,
    )

    plt.title(
        "RetailIQ Inventory Policy Comparison",
        fontsize=14,
        fontweight="bold",
    )

    plt.xlabel(
        "Store"
    )

    plt.ylabel(
        "Units"
    )

    plt.legend()

    plt.grid(
        axis="y",
        alpha=0.25,
    )

    plt.tight_layout()

    # ------------------------------------------------------
    # SAVE
    # ------------------------------------------------------

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
        "\nInventory visualization complete."
    )


if __name__ == "__main__":
    main()