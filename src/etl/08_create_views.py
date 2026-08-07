from pathlib import Path
import sqlite3
import time


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "database" / "RetailIQ.db"

SQL_PATH = (
    PROJECT_ROOT
    / "sql"
    / "03_create_views.sql"
)


def main():

    print("=" * 60)
    print("RETAILIQ VIEW CREATION")
    print("=" * 60)

    start = time.time()

    connection = sqlite3.connect(DATABASE_PATH)

    with open(SQL_PATH, "r", encoding="utf-8") as file:

        connection.executescript(file.read())

    connection.commit()

    connection.close()

    elapsed = time.time() - start

    print("\nViews created successfully!")

    print(f"\nCompleted in {elapsed:.2f} seconds")


if __name__ == "__main__":
    main()