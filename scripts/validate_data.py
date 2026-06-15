import os
import pandas as pd
import great_expectations as gx
from sqlalchemy import create_engine
from dotenv import load_dotenv


def get_orders_dataframe():
    load_dotenv()
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_NAME = os.getenv("POSTGRES_DB")
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@localhost:5432/{DB_NAME}"
    )
    df = pd.read_sql("SELECT * FROM olist_orders_dataset", engine)
    return df


def validate_orders(df):
    ge_df = gx.dataset.PandasDataset(df)
    results = []
    results.append(ge_df.expect_column_values_to_not_be_null("order_id"))
    results.append(ge_df.expect_column_values_to_be_unique("order_id"))
    results.append(ge_df.expect_column_values_to_not_be_null("customer_id"))
    valid_statuses = [
        "delivered", "shipped", "canceled", "unavailable",
        "invoiced", "processing", "created", "approved",
    ]
    results.append(
        ge_df.expect_column_values_to_be_in_set("order_status", valid_statuses)
    )
    return results


def print_results(results):
    print("\n" + "=" * 50)
    print("Data Quality Validation Results")
    print("=" * 50)
    all_passed = True
    for result in results:
        expectation = result.expectation_config.expectation_type
        success = result.success
        status = "PASS" if success else "FAIL"
        if not success:
            all_passed = False
        print(f"[{status}] {expectation}")
    print("=" * 50)
    print(f"Overall: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    print("=" * 50)


if __name__ == "__main__":
    df = get_orders_dataframe()
    print(f"Loaded {len(df)} rows from olist_orders_dataset")
    results = validate_orders(df)
    print_results(results)