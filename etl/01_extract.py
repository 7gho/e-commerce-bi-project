import sys
import io
import pandas as pd
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

RAW_DIR  = Path(__file__).parent.parent / "data" / "raw"
PROC_DIR = Path(__file__).parent.parent / "data" / "processed"
PROC_DIR.mkdir(parents=True, exist_ok=True)


def find_source_file():
    for pattern in ["*.xlsx", "*.xls", "*.csv"]:
        files = list(RAW_DIR.glob(pattern))
        if files:
            return files[0]
    print("Khong tim thay file dataset trong data/raw/")
    sys.exit(1)


def load_dataset(filepath):
    print(f"Loading: {filepath.name}")
    if filepath.suffix in [".xlsx", ".xls"]:
        try:
            sheets = pd.read_excel(filepath, sheet_name=None, dtype=str)
            df = pd.concat(sheets.values(), ignore_index=True)
            print(f"  Read {len(sheets)} sheet(s)")
        except Exception as e:
            print(f"  Multi-sheet failed ({e}), trying single sheet...")
            df = pd.read_excel(filepath, dtype=str)
    else:
        df = pd.read_csv(filepath, dtype=str, encoding="utf-8", encoding_errors="replace")
    return df


def extract():
    filepath = find_source_file()
    df = load_dataset(filepath)

    print(f"\nRows: {len(df):,}")
    print(f"Cols: {list(df.columns)}")

    # check nulls
    for col in df.columns:
        n = df[col].isna().sum()
        if n > 0:
            print(f"  {col}: {n:,} nulls ({n/len(df)*100:.1f}%)")

    out = PROC_DIR / "retail_raw.csv"
    df.to_csv(out, index=False, encoding="utf-8")
    print(f"\nSaved to {out}")
    return df


if __name__ == "__main__":
    extract()
