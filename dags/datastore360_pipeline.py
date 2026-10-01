from datetime import datetime

from airflow.sdk import dag, task

RAW_FILE = "/opt/airflow/data/raw/store-data-6aa6d7a3f171f140353680.csv"
CLEAN_FILE = "/opt/airflow/data/processed/clean_data.csv"
CONNECTION_ID = "datastore360_db"

@dag(
    dag_id="datastore360_pipeline",
    description="CSV -> staging -> cleaning and pseudonymization -> core",
    schedule=None,
    start_date=datetime(2026, 1, 1),
)
def datastore360_pipeline():

    @task
    def create_tables():
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from datastore360.db import run_sql_folder

        run_sql_folder(PostgresHook(postgres_conn_id=CONNECTION_ID).get_sqlalchemy_engine())
        return True

    @task
    def extract(tables_ready):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from datastore360.extract import read_raw_data
        from datastore360.load import load_to_staging

        df = read_raw_data(RAW_FILE)
        engine = PostgresHook(postgres_conn_id=CONNECTION_ID).get_sqlalchemy_engine()
        load_to_staging(df, engine)

        return df

    @task
    def transform(raw_df):
        from datastore360.cleaning import clean_data
        from datastore360.pseudonymize import pseudonymize_customer_names
        from datastore360.transform import transform_data

        df = transform_data(pseudonymize_customer_names(clean_data(raw_df)))
        df.to_csv(CLEAN_FILE, index=False)

        return df

    @task
    def load_all(clean_df):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from datastore360.load import load_core
        from datastore360.transform import split_tables

        engine = PostgresHook(postgres_conn_id=CONNECTION_ID).get_sqlalchemy_engine()
        customers, products, orders = split_tables(clean_df)

        return load_core(customers, products, orders, engine)

    tables_ready = create_tables()
    raw_df = extract(tables_ready)
    clean_df = transform(raw_df)
    load_all(clean_df)

datastore360_pipeline()
