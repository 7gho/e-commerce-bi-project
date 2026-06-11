import sys
import io
import pandas as pd
import numpy as np
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROC_DIR = Path(__file__).parent.parent / "data" / "processed"

# country -> (region, continent)
REGION_MAP = {
    "United Kingdom": ("Western Europe", "Europe"),
    "Germany":        ("Western Europe", "Europe"),
    "France":         ("Western Europe", "Europe"),
    "Netherlands":    ("Western Europe", "Europe"),
    "Belgium":        ("Western Europe", "Europe"),
    "Switzerland":    ("Western Europe", "Europe"),
    "Austria":        ("Western Europe", "Europe"),
    "Ireland":        ("Western Europe", "Europe"),
    "Portugal":       ("Western Europe", "Europe"),
    "Spain":          ("Western Europe", "Europe"),
    "Italy":          ("Western Europe", "Europe"),
    "Luxembourg":     ("Western Europe", "Europe"),
    "Denmark":        ("Northern Europe", "Europe"),
    "Norway":         ("Northern Europe", "Europe"),
    "Sweden":         ("Northern Europe", "Europe"),
    "Finland":        ("Northern Europe", "Europe"),
    "Iceland":        ("Northern Europe", "Europe"),
    "Poland":         ("Eastern Europe", "Europe"),
    "Czech Republic": ("Eastern Europe", "Europe"),
    "Lithuania":      ("Eastern Europe", "Europe"),
    "Cyprus":         ("Southern Europe", "Europe"),
    "Malta":          ("Southern Europe", "Europe"),
    "Greece":         ("Southern Europe", "Europe"),
    "United States":  ("North America", "Americas"),
    "Canada":         ("North America", "Americas"),
    "Brazil":         ("South America", "Americas"),
    "Japan":          ("East Asia", "Asia"),
    "China":          ("East Asia", "Asia"),
    "Singapore":      ("Southeast Asia", "Asia"),
    "Hong Kong":      ("East Asia", "Asia"),
    "Israel":         ("Middle East", "Asia"),
    "Bahrain":        ("Middle East", "Asia"),
    "Saudi Arabia":   ("Middle East", "Asia"),
    "United Arab Emirates": ("Middle East", "Asia"),
    "Lebanon":        ("Middle East", "Asia"),
    "Australia":      ("Oceania", "Oceania"),
    "South Africa":   ("Africa", "Africa"),
    "Nigeria":        ("Africa", "Africa"),
    "Unspecified":    ("Unknown", "Unknown"),
    "European Community": ("Western Europe", "Europe"),
}

COUNTRY_RENAME = {
    "EIRE":            "Ireland",
    "RSA":             "South Africa",
    "USA":             "United States",
    "Channel Islands": "United Kingdom",
}


def normalize_columns(df):
    rename_map = {
        "Invoice":     "InvoiceNo",
        "Price":       "UnitPrice",
        "Customer ID": "CustomerID",
    }
    return df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})


def clean_data(df):
    print(f"  Rows: {len(df):,}")

    df["Quantity"]    = pd.to_numeric(df["Quantity"],  errors="coerce")
    df["UnitPrice"]   = pd.to_numeric(df["UnitPrice"], errors="coerce")
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")

    df = df.dropna(subset=["InvoiceDate", "StockCode", "UnitPrice"])

    df["InvoiceNo"] = df["InvoiceNo"].astype(str).str.strip()
    df["is_return"] = df["InvoiceNo"].str.startswith("C")

    # drop zero-price non-return rows
    df = df[~((df["UnitPrice"] <= 0) & (df["is_return"] == False))]

    df["CustomerID"] = df["CustomerID"].fillna("GUEST").astype(str).str.strip()
    df["CustomerID"] = df["CustomerID"].str.replace(r"\.0$", "", regex=True)

    df["Description"] = df["Description"].fillna("Unknown").astype(str).str.strip().str.title()
    df["Country"]     = df["Country"].fillna("Unspecified").astype(str).str.strip()
    df["Country"]     = df["Country"].replace(COUNTRY_RENAME)

    df["total_amount"] = df["Quantity"] * df["UnitPrice"]

    print(f"  After cleaning: {len(df):,}")
    return df


def build_dim_region(df):
    records = []
    for country in df["Country"].unique():
        region, continent = REGION_MAP.get(country, ("Other", "Other"))
        records.append({"country": country, "region": region, "continent": continent})
    dim = pd.DataFrame(records).drop_duplicates()
    dim.insert(0, "region_key", range(1, len(dim) + 1))
    print(f"  dim_region: {len(dim)}")
    return dim


def build_dim_customer(df):
    dim = (
        df[["CustomerID", "Country"]]
        .drop_duplicates()
        .rename(columns={"CustomerID": "customer_id", "Country": "country"})
    )
    dim["region"] = dim["country"].map(lambda x: REGION_MAP.get(x, ("Other",))[0])
    dim.insert(0, "customer_key", range(1, len(dim) + 1))
    print(f"  dim_customer: {len(dim)}")
    return dim


def build_dim_product(df):
    most_common = (
        df.groupby("StockCode")["Description"]
        .agg(lambda x: x.value_counts().index[0])
        .reset_index()
    )
    dim = most_common.rename(columns={"StockCode": "stock_code", "Description": "description"})
    dim["category"] = "General"
    dim.insert(0, "product_key", range(1, len(dim) + 1))
    print(f"  dim_product: {len(dim)}")
    return dim


def build_dim_time(df):
    min_date = df["InvoiceDate"].dt.normalize().min()
    max_date = df["InvoiceDate"].dt.normalize().max()
    dates = pd.date_range(start=min_date, end=max_date, freq="D")

    dim = pd.DataFrame({"full_date": dates})
    dim["day"]        = dim["full_date"].dt.day
    dim["month"]      = dim["full_date"].dt.month
    dim["month_name"] = dim["full_date"].dt.strftime("%B")
    dim["quarter"]    = dim["full_date"].dt.quarter
    dim["year"]       = dim["full_date"].dt.year
    dim["day_of_week"]= dim["full_date"].dt.strftime("%A")
    dim["is_weekend"] = dim["full_date"].dt.dayofweek >= 5
    dim.insert(0, "time_key", range(1, len(dim) + 1))
    print(f"  dim_time: {len(dim)} ({min_date.date()} to {max_date.date()})")
    return dim


def build_fact_orders(df, dim_customer, dim_product, dim_time, dim_region):
    cust_map   = dim_customer.set_index(["customer_id", "country"])["customer_key"].to_dict()
    prod_map   = dim_product.set_index("stock_code")["product_key"].to_dict()
    time_map   = dim_time.set_index("full_date")["time_key"].to_dict()
    region_map = dim_region.set_index("country")["region_key"].to_dict()

    fact = df.copy()
    fact["date_only"]    = fact["InvoiceDate"].dt.normalize()
    fact["customer_key"] = fact.apply(lambda r: cust_map.get((r["CustomerID"], r["Country"])), axis=1)
    fact["product_key"]  = fact["StockCode"].map(prod_map)
    fact["time_key"]     = fact["date_only"].map(time_map)
    fact["region_key"]   = fact["Country"].map(region_map)

    fact_final = fact[[
        "InvoiceNo", "customer_key", "product_key",
        "time_key", "region_key",
        "Quantity", "UnitPrice", "total_amount", "is_return"
    ]].rename(columns={
        "InvoiceNo": "invoice_no",
        "Quantity":  "quantity",
        "UnitPrice": "unit_price",
    })

    fact_final = fact_final.dropna(subset=["product_key", "time_key"])
    print(f"  fact_orders: {len(fact_final):,}")
    return fact_final


def transform():
    print("Transform started")

    raw_path = PROC_DIR / "retail_raw.csv"
    if not raw_path.exists():
        print("retail_raw.csv not found. Run 01_extract.py first.")
        return

    df = pd.read_csv(raw_path, dtype=str)
    df = normalize_columns(df)
    df = clean_data(df)

    dim_region   = build_dim_region(df)
    dim_customer = build_dim_customer(df)
    dim_product  = build_dim_product(df)
    dim_time     = build_dim_time(df)
    fact_orders  = build_fact_orders(df, dim_customer, dim_product, dim_time, dim_region)

    dim_region.to_csv(PROC_DIR / "dim_region.csv",   index=False)
    dim_customer.to_csv(PROC_DIR / "dim_customer.csv", index=False)
    dim_product.to_csv(PROC_DIR / "dim_product.csv",  index=False)
    dim_time.to_csv(PROC_DIR / "dim_time.csv",        index=False)
    fact_orders.to_csv(PROC_DIR / "fact_orders.csv",  index=False)

    print("Done. Saved to data/processed/")
    return dim_region, dim_customer, dim_product, dim_time, fact_orders


if __name__ == "__main__":
    transform()
