import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

load_dotenv()

SQL_FOLDER = Path(__file__).resolve().parents[2] / "include" / "sql"

def get_engine():
    url = URL.create(
        "postgresql+psycopg2",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        database=os.environ["POSTGRES_DB"],
    )

    return create_engine(url)

def run_sql_file(engine, path):
    with engine.begin() as conn:
        conn.exec_driver_sql(Path(path).read_text(encoding="utf-8"))

def run_sql_folder(engine, folder=SQL_FOLDER):
    for path in sorted(Path(folder).glob("*.sql")):
        run_sql_file(engine, path)