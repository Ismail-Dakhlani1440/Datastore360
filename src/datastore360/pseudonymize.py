import hashlib
import os

from dotenv import load_dotenv

load_dotenv()

def pseudonymize_customer_names(df):
    salt = os.environ["RGPD_HASH_SALT"]
    df["Customer Name"] = df["Customer Name"].map(
        lambda name: hashlib.sha256((name + salt).encode("utf-8")).hexdigest()
    )

    return df