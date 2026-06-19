-- Star Schema - стандарта проектирования DWH.
-- `dim` — dimension (измерение). Это справочные таблицы, которые описывают кто и что. 
-- `fact` — fact (факт). Это таблицы событий, которые фиксируют что произошло в конкретный момент времени.


CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id INTEGER PRIMARY KEY,
    full_name TEXT,
    email TEXT,
    phone TEXT,
    city TEXT,
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    price NUMERIC(10, 2),
    currency TEXT,
    is_active BOOLEAN
);

CREATE TABLE IF NOT EXISTS fact_orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES dim_customers(customer_id),
    product_id INTEGER REFERENCES dim_products(product_id),
    quantity INTEGER,
    unit_price NUMERIC(10, 2),
    amount NUMERIC(10, 2),
    currency TEXT,
    order_timestamp TIMESTAMP,
    status TEXT
);

CREATE TABLE IF NOT EXISTS fact_payments (
    payment_id INTEGER PRIMARY KEY,
    order_id INTEGER REFERENCES fact_orders(order_id),
    payment_method TEXT,
    amount NUMERIC(10, 2),
    currency TEXT,
    payment_timestamp TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fact_events (
    event_id TEXT,
    customer_id TEXT,
    event_type TEXT,
    event_timestamp TIMESTAMP,
    product_id TEXT
);