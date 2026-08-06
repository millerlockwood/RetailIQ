from pathlib import Path
import pandas as pd

# ----------------------------
# Project Paths
# ----------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "raw"

# ----------------------------
# Files
# ----------------------------

calendar = pd.read_csv(DATA_PATH / "calendar.csv")
sales = pd.read_csv(DATA_PATH / "sales_train_validation.csv")
prices = pd.read_csv(DATA_PATH / "sell_prices.csv")

datasets = {
    "Calendar": calendar,
    "Sales": sales,
    "Prices": prices
}

print("=" * 60)
print("RETAILIQ DATA OVERVIEW")
print("=" * 60)

for name, df in datasets.items():

    print(f"\n{name}")
    print("-" * 60)

    print(f"Rows: {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumn Types")
    print(df.dtypes)

    print("\nMissing Values")
    print(df.isna().sum())

    print("\nFirst Five Rows")
    print(df.head())

    print("\nMemory Usage")
    print(f"{df.memory_usage(deep=True).sum()/1024**2:.2f} MB")

print("\nData profiling complete.")