from pathlib import Path
import sqlite3
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "database" / "RetailIQ.db"

OUTPUT_PATH = PROJECT_ROOT / "reports" / "executive_kpis.csv"


def query_value(connection, sql):
    return pd.read_sql_query(sql, connection).iloc[0, 0]


def main():

    connection = sqlite3.connect(DATABASE_PATH)

    data = {

        "Total Units Sold":
            query_value(
                connection,
                """
                SELECT SUM(total_units_sold)
                FROM summary_store_sales;
                """
            ),

        "Number of Products":
            query_value(
                connection,
                """
                SELECT COUNT(*)
                FROM dim_product;
                """
            ),

        "Number of Stores":
            query_value(
                connection,
                """
                SELECT COUNT(*)
                FROM dim_store;
                """
            ),

        "Number of States":
            query_value(
                connection,
                """
                SELECT COUNT(DISTINCT state_id)
                FROM dim_store;
                """
            ),

        "Top Store":
            query_value(
                connection,
                """
                SELECT store_id
                FROM summary_store_sales
                ORDER BY total_units_sold DESC
                LIMIT 1;
                """
            ),

        "Top State":
            query_value(
                connection,
                """
                SELECT state_id
                FROM summary_state_sales
                ORDER BY total_units_sold DESC
                LIMIT 1;
                """
            ),

        "Top Product":
            query_value(
                connection,
                """
                SELECT item_id
                FROM summary_product_sales
                ORDER BY total_units_sold DESC
                LIMIT 1;
                """
            ),

        "Top Category":
            query_value(
                connection,
                """
                SELECT cat_id
                FROM summary_category_sales
                ORDER BY total_units_sold DESC
                LIMIT 1;
                """
            ),
    }

    connection.close()

    dataframe = pd.DataFrame([data])

    dataframe.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(dataframe)


if __name__ == "__main__":
    main()