import pandas as pd

def fix_date_columns(df):
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='mixed', errors='coerce')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'] , format='mixed' , errors='coerce')

    return df

def format_data(df):
    id_cols = ["Row ID", "Order ID", "Customer ID", "Product ID"]
    string_cols = df.select_dtypes(include="object").columns.difference(id_cols)
    for col in string_cols:
        df[col] = df[col].str.strip().str.lower()

    return df

def fix_customer_id_case(df):
    df["Customer ID"] = df["Customer ID"].str.upper()

    return df
    
def fix_segment_typos(df):
    typo_map = {
        "consumerr": "consumer",
        "corporrate": "corporate",
        "home ofice": "home office",
    }
    df["Segment"] = df["Segment"].replace(typo_map)

    return df

def fill_empty_names(df):
    invalid_customers = df["Customer Name"].isna()
    customer_name_by_id = df.groupby("Customer ID")["Customer Name"].agg(lambda x:x.mode().iloc[0] if not x.mode().empty else pd.NA)
    df.loc[invalid_customers, "Customer Name"] = df.loc[invalid_customers, "Customer ID"].map(customer_name_by_id)

    return df

def drop_rows_without_customer_name(df):
    missing_name = df["Customer Name"].isna()

    return df[~missing_name].copy()

def drop_tangled_product_rows(df):
    main_name = df.groupby("Product ID")["Product Name"].agg(lambda x: x.mode().iloc[0])
    other_product = df["Product Name"] != df["Product ID"].map(main_name)

    return df[~other_product].copy()

def null_invalid_ship_dates(df):
    invalid = df["Ship Date"] < df["Order Date"]
    df.loc[invalid, "Ship Date"] = pd.NaT

    return df

def fill_dates_and_ship_mode_and_postal_code_by_mode(df):
    for col in ["Ship Date","Ship Mode","Postal Code"]:
        mode_by_order = df.groupby("Order ID")[col].agg(lambda x: x.mode().iloc[0] if not x.mode().empty else pd.NA)
        df[col] =df[col].fillna(df['Order ID'].map(mode_by_order))

    return df

def shipping_days_per_shipping_mode(mode):
    days_by_mode = {"same day": 0, "first class": 2, "second class": 3, "standard class": 5}
    return days_by_mode.get(mode)

def shipping_mode_per_shipping_days(days):
    if pd.isna(days) or days < 0:
            return None
    mode_by_days = {0: "same day", 1: "first class", 2: "second class", 3: "first class",
                    4: "standard class", 5: "standard class", 6: "standard class", 7: "standard class"}
    return mode_by_days.get(days)

def fix_remaining_shipping_dates(df):
    missing = df["Ship Date"].isna() & df["Ship Mode"].notna()
    days = df.loc[missing, "Ship Mode"].map(shipping_days_per_shipping_mode)
    df.loc[missing, "Ship Date"] = df.loc[missing, "Order Date"] + pd.to_timedelta(days, unit="D")

    return df

def fix_remaining_ship_modes(df):
    missing = df["Ship Mode"].isna() & df["Ship Date"].notna()
    days = (df.loc[missing, "Ship Date"] - df.loc[missing, "Order Date"]).dt.days
    df.loc[missing, "Ship Mode"] = days.map(shipping_mode_per_shipping_days)

    return df

def fix_postal_codes(df):
    df["Postal Code"] = df["Postal Code"].str.split(".").str[0]
    df["Postal Code"] = df["Postal Code"].str.zfill(5)

    return df

def fill_postal_codes_by_city(df):
    mode_by_city = df.groupby("City")["Postal Code"].agg(lambda x: x.mode().iloc[0] if not x.mode().empty else pd.NA)
    df["Postal Code"] = df["Postal Code"].fillna(df["City"].map(mode_by_city))

    return df

def drop_invalid_rows(df):
    invalid_sales = df["Sales"] == 1131924.0
    invalid_quantity = df["Quantity"] < 0
    invalid_discount = (df["Discount"] < 0) | (df["Discount"] > 1)
    both_missing = df["Sales"].isna() & df["Quantity"].isna()

    return df[~(invalid_sales | invalid_quantity | invalid_discount | both_missing)].copy()

def get_unit_price_by_product(df):
    df = df.copy()
    df["Unit Price"] = (df["Sales"] / (df["Quantity"] * (1 - df["Discount"]))).round(2)
    df = df.dropna(subset=["Unit Price"])
    price_by_product = df.groupby("Product ID")["Unit Price"].agg(lambda x: x.mode().iloc[0])

    return price_by_product

def drop_invalid_rows_2(df):
    price_by_product = get_unit_price_by_product(df)
    no_price = df["Product ID"].map(price_by_product).isna()
    both_missing = df["Sales"].isna() & df["Quantity"].isna()

    return df[~(no_price | both_missing)].copy()

def fill_missing_sales(df):
    price_by_product = get_unit_price_by_product(df)
    unit_price = df["Product ID"].map(price_by_product)
    rebuilt_sales = df["Quantity"] * (1 - df["Discount"]) * unit_price
    df["Sales"] = df["Sales"].fillna(rebuilt_sales.round(4))

    return df

def fill_missing_quantity(df):
    price_by_product = get_unit_price_by_product(df)
    unit_price = df["Product ID"].map(price_by_product)
    rebuilt_quantity = df["Sales"] / (unit_price * (1 - df["Discount"]))
    df["Quantity"] = df["Quantity"].fillna(rebuilt_quantity.round())
    return df

def convert_quantity_to_int(df):
    df["Quantity"] = df["Quantity"].astype(int)

    return df

def drop_duplicates(df):
    df.drop_duplicates

    return df

def clean_data(df):
    df = fix_date_columns(df)
    df = format_data(df)
    df = fix_customer_id_case(df)
    df = fix_segment_typos(df)
    df = fill_empty_names(df)
    df = drop_rows_without_customer_name(df)
    df = drop_tangled_product_rows(df)
    df = null_invalid_ship_dates(df)
    df = fill_dates_and_ship_mode_and_postal_code_by_mode(df)
    df = fix_remaining_shipping_dates(df)
    df = fix_remaining_ship_modes(df)
    df = fix_postal_codes(df)
    df = fill_postal_codes_by_city(df)
    df = drop_invalid_rows(df)
    df = drop_invalid_rows_2(df)
    df = fill_missing_sales(df)
    df = fill_missing_quantity(df)
    df = convert_quantity_to_int(df)
    df = drop_duplicates(df)

    return df