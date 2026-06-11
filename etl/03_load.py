import sys
import io
import os
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

load_dotenv(Path(__file__).parent.parent / ".env")

PROC_DIR = Path(__file__).parent.parent / "data" / "processed"
SQL_DIR  = Path(__file__).parent.parent / "sql"


def get_engine():
    url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER', 'postgres')}:"
        f"{os.getenv('DB_PASSWORD', '')}@{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'tmdt_bi')}"
    )
    return create_engine(url, echo=False)


def run_sql_file(engine, filepath):
    sql = filepath.read_text(encoding="utf-8")
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    print(f"  Ran: {filepath.name}")


def load_table(engine, df, table_name, chunk_size=5000):
    df.to_sql(table_name, engine, if_exists="append", index=False,
              chunksize=chunk_size, method="multi")
    print(f"  {table_name}: {len(df):,} rows")


def load():
    print("Loading to PostgreSQL...")
    engine = get_engine()

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("  Connected OK")
    except Exception as e:
        print(f"  Connection error: {e}")
        return

    run_sql_file(engine, SQL_DIR / "01_create_schema.sql")
    run_sql_file(engine, SQL_DIR / "02_indexes.sql")

    for filename, table in [
        ("dim_region.csv",   "dim_region"),
        ("dim_customer.csv", "dim_customer"),
        ("dim_product.csv",  "dim_product"),
        ("dim_time.csv",     "dim_time"),
    ]:
        load_table(engine, pd.read_csv(PROC_DIR / filename), table)

    load_table(engine, pd.read_csv(PROC_DIR / "fact_orders.csv"), "fact_orders")

    run_sql_file(engine, SQL_DIR / "03_views.sql")

    # verify
    with engine.connect() as conn:
        for t in ["dim_region", "dim_customer", "dim_product", "dim_time", "fact_orders"]:
            n = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            print(f"  {t}: {n:,}")

    print("Done.")


if __name__ == "__main__":
    load()
