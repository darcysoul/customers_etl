import sys
import os
import json
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'dq_issues.json')


def task_create_schema(**context):
    """Создаем таблицы"""
    from load import get_engine, create_schema
    engine = get_engine()
    create_schema(engine)


def task_extract(**context):
    """Читаем все источники"""
    from extract import extract_all
    raw = extract_all(DATA_DIR)
    # DataFrames сериализуем в JSON
    serialized = {k: v.to_json(orient='records', date_format='iso')
                  for k, v in raw.items()}
    context['ti'].xcom_push(key='raw_data', value=serialized)
    print(f"[EXTRACT] Загружено источников: {len(raw)}")
    for name, df in raw.items():
        print(f"  {name}: {len(df)} строк")


def task_transform(**context):
    """Очищаем данные, логируем проблемы"""
    import pandas as pd
    from transform import transform_all

    serialized = context['ti'].xcom_pull(key='raw_data', task_ids='extract')
    raw = {k: pd.read_json(v, orient='records') for k, v in serialized.items()}
    cleaned, issues = transform_all(raw)

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(issues, f, ensure_ascii=False, indent=2, default=str)
    print(f"[TRANSFORM] Проблем найдено: {len(issues)}")

    serialized_clean = {k: v.to_json(orient='records', date_format='iso')
                        for k, v in cleaned.items()}
    context['ti'].xcom_push(key='cleaned_data', value=serialized_clean)
    for name, df in cleaned.items():
        print(f"  {name}: {len(df)} строк после очистки")


def task_load(**context):
    """Загружаем очищенные данные в PostgreSQL"""
    import pandas as pd
    from load import load_all

    serialized = context['ti'].xcom_pull(key='cleaned_data', task_ids='transform')
    cleaned = {k: pd.read_json(v, orient='records') for k, v in serialized.items()}

    load_all(cleaned)
    print("[LOAD] Все данные загружены в PostgreSQL")


with DAG(
    dag_id='0_etl_pipeline',
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=['etl', 'part3', 'it-gorod'],
) as dag:

    extract = PythonOperator(
        task_id='extract',
        python_callable=task_extract,
    )

    transform = PythonOperator(
        task_id='transform',
        python_callable=task_transform,
    )

    load = PythonOperator(
        task_id='load',
        python_callable=task_load,
    )

    create_schema_task = PythonOperator(
        task_id='create_schema',
        python_callable=task_create_schema,
    )

    create_schema_task >> extract >> transform >> load
