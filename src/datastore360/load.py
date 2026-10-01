import pandas as pd
from sqlalchemy import text

COLUMNS = [
    "Row ID", "Order ID", "Order Date", "Ship Date", "Ship Mode", "Customer ID", "Customer Name",
    "Segment", "Country", "City", "State", "Postal Code", "Region", "Product ID", "Category",
    "Sub-Category", "Product Name", "Sales", "Quantity", "Discount", "Profit",
]

def load_to_staging(df, engine):
    df.columns = [name.lower().replace(" ", "_").replace("-", "_") for name in df.columns]
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE staging.superstore_raw"))
        df.to_sql("superstore_raw", conn, schema="staging", if_exists="append", index=False)

    return len(df)

def read_from_staging(engine):
    df = pd.read_sql("SELECT * FROM staging.superstore_raw ORDER BY row_id::integer", engine)
    df.columns = COLUMNS
    for column in ["Row ID", "Sales", "Quantity", "Discount", "Profit"]:
        df[column] = pd.to_numeric(df[column])

    return df

def load_core(customers, products, orders, engine):
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE core.orders, core.customers, core.products"))
        customers.to_sql("customers", conn, schema="core", if_exists="append", index=False)
        products.to_sql("products", conn, schema="core", if_exists="append", index=False)
        orders.to_sql("orders", conn, schema="core", if_exists="append", index=False)

    return len(customers), len(products), len(orders)
