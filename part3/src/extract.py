import pandas as pd
import json
import xml.etree.ElementTree as ET


def extract_customers(path):
    return pd.read_csv(path)


def extract_orders(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return pd.DataFrame(data)


def extract_products(path):
    return pd.read_excel(path, engine='openpyxl')


# парсинг XML-файл в DataFrame Pandas
# https://www.reddit.com/r/learnpython/comments/zh9vgw/parsing_xml_into_a_pandas_dataframe/?tl=ru
# https://docs.python.org/3/library/xml.etree.elementtree.html
def extract_events(path):
    tree = ET.parse(path)
    root = tree.getroot()
    rows = []
    for event in root:
        row = {child.tag: child.text for child in event}
        rows.append(row)
    return pd.DataFrame(rows)


def extract_payments(path):
    return pd.read_csv(path, sep='^')


def extract_all(data_dir):
    return {
        'customers': extract_customers(f'{data_dir}/customers.csv'),
        'orders':    extract_orders(f'{data_dir}/orders.json'),
        'products':  extract_products(f'{data_dir}/products.xlsx'),
        'events':    extract_events(f'{data_dir}/events.xml'),
        'payments':  extract_payments(f'{data_dir}/payments.csv'),
    }
