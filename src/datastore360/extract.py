import pandas as pd

def read_raw_data(path):
    df = pd.read_csv(path, dtype=str)
    return df



