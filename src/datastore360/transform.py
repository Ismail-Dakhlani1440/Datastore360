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
