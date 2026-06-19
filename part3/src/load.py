import pandas as pd
from sqlalchemy import create_engine, text

DB_URL = "postgresql://postgres:postgres@etl-postgres:5432/etl_db"


def get_engine():
    return create_engine(DB_URL)


def create_schema(engine):
    ddl_path = '/opt/airflow/ddl/schema.sql'
    with open(ddl_path, 'r') as f:
        ddl = f.read()
    with engine.connect() as conn:
        conn.execute(text(ddl))
        conn.commit()
    print("[OK] Схема создана")


def load_table(df, table_name, engine, if_exists='append'):
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists=if_exists,
        index=False,
        method='multi'
    )
    print(f"[OK] {table_name}: загружено {len(df)} строк")


def clear_tables(engine):
    with engine.connect() as conn:
        # Порядок важен из-за foreign keys
        # без каскадного удаления dag упадет
        conn.execute(text("TRUNCATE TABLE fact_events RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE fact_payments RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE fact_orders RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE dim_products RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE dim_customers RESTART IDENTITY CASCADE"))
        conn.commit()
    print("[OK] Таблицы очищены")


def load_all(cleaned: dict):
    engine = get_engine()
    clear_tables(engine)

    load_table(cleaned['customers'], 'dim_customers', engine)
    load_table(cleaned['products'],  'dim_products',  engine)
    load_table(cleaned['orders'],    'fact_orders',   engine)
    load_table(cleaned['payments'],  'fact_payments', engine)
    load_table(cleaned['events'],    'fact_events',   engine)
