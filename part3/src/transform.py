import pandas as pd
import re


def log_issue(issues, source, row_id, issue, data):
    issues.append({
        'source': source,
        'row_id': str(row_id),
        'issue': issue,
        'data': {k: str(v) for k, v in data.items()}
    })


def clean_customers(df):
    issues = []
    df = df.copy()

    def normalize_phone(p):
        if pd.isna(p) or str(p).strip() in ('', 'UNKNOWN'):
            return None
        p = str(p).replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if p.startswith('8') and len(p) == 11:
            p = '+7' + p[1:]
        elif not p.startswith('+'):
            p = '+7' + p
        return p

    df['phone'] = df['phone'].apply(normalize_phone)

    no_email = df[df['email'].isna()]
    for _, row in no_email.iterrows():
        log_issue(issues, 'customers', row['customer_id'],
                  'missing email', row.to_dict())

    df = df.drop_duplicates(subset=['customer_id'])
    df['email'] = df['email'].str.strip().str.lower()

    prefixes = r'^(г-н|г-жа|проф\.|д-р|mr\.|mrs\.|ms\.)\s+'
    df['full_name'] = (df['full_name']
                       .str.strip()
                       .str.replace(prefixes, '', regex=True, flags=re.IGNORECASE)
                       .str.strip()
                       )

    df['full_name'] = df['full_name'].str.title()

    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')

    # Логируем невалидные даты
    bad_dates = df[df['created_at'].isna()]
    for _, row in bad_dates.iterrows():
        log_issue(issues, 'customers', row['customer_id'],
                  'invalid created_at', row.to_dict())

    return df, issues


def clean_products(df):
    issues = []
    df = df.copy()
    df = df.drop_duplicates(subset=['product_id'])
    df['price'] = pd.to_numeric(df['price'], errors='coerce')

    no_price = df[df['price'].isna()]
    for _, row in no_price.iterrows():
        log_issue(issues, 'products', row['product_id'],
                  'missing price', row.to_dict())

    df = df.dropna(subset=['product_id'])
    return df, issues


def clean_orders(df, valid_product_ids, valid_customer_ids):
    issues = []
    df = df.copy()

    df['amount'] = pd.to_numeric(df['quantity'], errors='coerce') * \
                   pd.to_numeric(df['unit_price'], errors='coerce')

    df['order_timestamp'] = pd.to_datetime(df['order_timestamp'], errors='coerce')

    bad_dates = df[df['order_timestamp'].isna()]
    for _, row in bad_dates.iterrows():
        log_issue(issues, 'orders', row['order_id'],
                  'invalid order_timestamp', row.to_dict())

    df = df.drop_duplicates(subset=['order_id'])
    df = df.dropna(subset=['order_id', 'customer_id'])

    # заказы с product_id, которого нет в dim_products
    unknown_products = df[~df['product_id'].isin(valid_product_ids)]
    for _, row in unknown_products.iterrows():
        log_issue(issues, 'orders', row['order_id'],
                  'unknown product_id — not in dim_products', row.to_dict())
    df = df[df['product_id'].isin(valid_product_ids)]

    # заказы с customer_id, которого нет в dim_customers
    unknown_customers = df[~df['customer_id'].isin(valid_customer_ids)]
    for _, row in unknown_customers.iterrows():
        log_issue(issues, 'orders', row['order_id'],
                  'unknown customer_id — not in dim_customers', row.to_dict())
    df = df[df['customer_id'].isin(valid_customer_ids)]

    return df, issues


def clean_payments(df, valid_order_ids):
    issues = []
    df = df.copy()

    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

    bad_amount = df[df['amount'].isna()]
    for _, row in bad_amount.iterrows():
        log_issue(issues, 'payments', row['payment_id'],
                  'invalid amount', row.to_dict())

    df['payment_timestamp'] = pd.to_datetime(
        df['payment_timestamp'], errors='coerce'
    )
    bad_dates = df[df['payment_timestamp'].isna()]
    for _, row in bad_dates.iterrows():
        log_issue(issues, 'payments', row['payment_id'],
                  'invalid payment_timestamp', row.to_dict())

    df['payment_method'] = df['payment_method'].fillna('unknown').replace('', 'unknown')

    df = df.drop_duplicates(subset=['payment_id'])
    df = df.dropna(subset=['payment_id', 'order_id'])

    # платежи с order_id, которого нет в fact_orders
    unknown_orders = df[~df['order_id'].isin(valid_order_ids)]
    for _, row in unknown_orders.iterrows():
        log_issue(issues, 'payments', row['payment_id'],
                  'unknown order_id — not in fact_orders', row.to_dict())
    df = df[df['order_id'].isin(valid_order_ids)]

    return df, issues


def clean_events(df, valid_customer_ids):
    issues = []
    df = df.copy()

    bad_ids = df[df['event_id'].isna() | df['customer_id'].isna()]
    for _, row in bad_ids.iterrows():
        log_issue(issues, 'events', row.get('event_id', 'UNKNOWN'),
                  'missing event_id or customer_id', row.to_dict())
    df = df.dropna(subset=['event_id', 'customer_id'])

    df['event_timestamp'] = pd.to_datetime(df['event_timestamp'], errors='coerce')
    bad_dates = df[df['event_timestamp'].isna()]
    for _, row in bad_dates.iterrows():
        log_issue(issues, 'events', row['event_id'],
                  'invalid event_timestamp', row.to_dict())

    phantoms = df[df['customer_id'] == '999999']
    for _, row in phantoms.iterrows():
        log_issue(issues, 'events', row['event_id'],
                  'phantom customer_id=999999', row.to_dict())

    # события с customer_id, которого нет в dim_customers
    unknown_customers = df[~df['customer_id'].isin(valid_customer_ids)]
    for _, row in unknown_customers.iterrows():
        log_issue(issues, 'events', row['event_id'],
                  'unknown customer_id — not in dim_customers', row.to_dict())
    df = df[df['customer_id'].isin(valid_customer_ids)]

    return df, issues


def transform_all(raw):
    all_issues = []
    cleaned = {}

    cleaned['customers'], issues = clean_customers(raw['customers'])
    all_issues.extend(issues)

    cleaned['products'], issues = clean_products(raw['products'])
    all_issues.extend(issues)

    valid_customer_ids = set(cleaned['customers']['customer_id'].dropna().astype(int))
    valid_product_ids = set(cleaned['products']['product_id'].dropna().astype(int))

    cleaned['orders'], issues = clean_orders(
        raw['orders'], valid_product_ids, valid_customer_ids
    )
    all_issues.extend(issues)

    valid_order_ids = set(cleaned['orders']['order_id'].dropna().astype(int))

    cleaned['payments'], issues = clean_payments(raw['payments'], valid_order_ids)
    all_issues.extend(issues)

    cleaned['events'], issues = clean_events(raw['events'], valid_customer_ids)
    all_issues.extend(issues)

    return cleaned, all_issues
