from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "RetailIQ.db"

SQL_PATH = (
    PROJECT_ROOT
    / "sql"
    / "01_create_tables.sql"
)


def main():

    print("=" * 60)
    print("RETAILIQ DATABASE BUILD")
    print("=" * 60)

    print("\nCreating database...")

    connection = sqlite3.connect(DATABASE_PATH)

    with open(SQL_PATH, "r", encoding="utf-8") as file:
        sql_script = file.read()

    connection.executescript(sql_script)

    connection.commit()

    connection.close()

    print("\nDatabase created successfully!")

    print(DATABASE_PATH)


if __name__ == "__main__":
    main()