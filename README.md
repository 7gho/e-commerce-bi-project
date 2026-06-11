# E-commerce BI Project - Group 13 

Analyzing online retail transaction data using Python + PostgreSQL + Power BI.
Dataset: Online Retail II (UCI) — 1,061,165 transaction rows from 2009–2011.

## Workflow

**Requirements:** Python 3.x, PostgreSQL, Power BI Desktop

```bash
pip install -r requirements.txt
```

Create a `.env` file from `.env.example`, and fill in the PostgreSQL connection information. Create the `tmdt_bi` database in pgAdmin.

The dataset is already in `data/raw/`. Run the ETL in the following order:

```bash
python etl/01_extract.py
python etl/02_transform.py
python etl/03_load.py
```

After that, open `dashboard/tmdt_bi.pbix` using Power BI Desktop.

## Structure

```
etl/        Python scripts (extract, transform, load)
sql/        Schema, indexes, views
docs/       Reports
dashboard/  Power BI file
data/raw/   Original dataset
```