import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv


def load_csvs_to_postgres():
    # .env 로드
    load_dotenv()

    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_NAME = os.getenv("POSTGRES_DB")
    DB_HOST = "localhost"
    DB_PORT = "5432"

    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    DATA_DIR = "data/raw"
    csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]

    for csv_file in csv_files:
        table_name = csv_file.replace(".csv", "")
        file_path = os.path.join(DATA_DIR, csv_file)

        print(f"Loading {csv_file} -> table '{table_name}' ...")
        df = pd.read_csv(file_path)
        df.to_sql(table_name, engine, if_exists="replace", index=False)
        print(f"  -> {len(df)} rows loaded.")

    print("All done.")


if __name__ == "__main__":
    load_csvs_to_postgres()