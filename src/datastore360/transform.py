def add_delivery_time(df):
    df["Delivery Time"] = (df["Ship Date"] - df["Order Date"]).dt.days

    return df

def add_profit_margin(df):
    df["Profit Margin"] = (df["Profit"] / df["Sales"]).round(4)

    return df

def add_unit_price(df):
    df["Unit Price"] = (df["Sales"] / (df["Quantity"] * (1 - df["Discount"]))).round(2)

    return df

def transform_data(df):
    df = add_delivery_time(df)
    df = add_profit_margin(df)
    df = add_unit_price(df)

    return df

def split_tables(df):
    customers = df.drop_duplicates("Customer ID")[["Customer ID", "Customer Name", "Segment", "Country", "City", "State", "Postal Code", "Region"]]
    customers.columns = ["customerid", "customername", "segment", "country", "city", "state", "postal_code", "region"]

    products = df.drop_duplicates("Product ID")[["Product ID", "Category", "Sub-Category", "Product Name", "Unit Price"]]
    products.columns = ["productid", "category", "subcategory", "product_name", "unit_price"]

    orders = df[["Row ID", "Order ID", "Customer ID", "Product ID", "Order Date", "Ship Date", "Ship Mode", "Sales", "Quantity",
                 "Discount", "Profit", "Delivery Time", "Profit Margin", "City", "State", "Postal Code", "Region"]]
    orders.columns = ["rowid", "orderid", "customerid", "productid", "orderdate", "shipdate", "shipmode", "sales", "quantity",
                      "discount", "profit", "deliverytime", "profit_margin", "ship_city", "ship_state", "ship_postal_code", "ship_region"]

    return customers, products, orders
