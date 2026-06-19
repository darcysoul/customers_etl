-- Топ-10 клиентов по сумме покупок
SELECT
    c.customer_id,
    c.full_name,
    SUM(o.amount) AS total_amount
FROM dim_customers c
JOIN fact_orders o ON o.customer_id = c.customer_id
WHERE o.status != 'cancelled'
GROUP BY c.customer_id, c.full_name
ORDER BY total_amount DESC
LIMIT 10;


-- Выручка по месяцам
SELECT
    TO_CHAR(o.order_timestamp, 'YYYY-MM') AS year_month,
    COUNT(o.order_id) AS order_count,
    SUM(o.amount) AS revenue
FROM fact_orders o
WHERE o.order_timestamp IS NOT NULL
  AND o.status != 'cancelled'
GROUP BY year_month
ORDER BY year_month;


-- Самые популярные товары
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.price,
    COUNT(o.order_id)   AS order_count,
    SUM(o.quantity)     AS total_quantity_sold,
    SUM(o.amount)       AS total_revenue
FROM dim_products p
JOIN fact_orders o ON o.product_id = p.product_id
WHERE o.status != 'cancelled'
GROUP BY p.product_id, p.product_name, p.category, p.price
ORDER BY order_count DESC
LIMIT 10;


-- Последняя активность топ-5 покупателей
WITH top5_buyers AS (
    SELECT
        customer_id,
        COUNT(order_id) AS purchase_count
    FROM fact_orders
    WHERE status != 'cancelled'
    GROUP BY customer_id
    ORDER BY purchase_count DESC
    LIMIT 5
)
SELECT
    c.customer_id,
    c.full_name,
    t.purchase_count,
    MAX(e.event_timestamp) AS last_activity_date,
    (
        SELECT event_type
        FROM fact_events
        -- поскольку в fact_events колонка customer_id 
        -- типа text нужно преобразование в int
        WHERE customer_id::int = c.customer_id
          AND event_timestamp = MAX(e.event_timestamp)
        LIMIT 1
    ) AS last_event_type
FROM top5_buyers t
JOIN dim_customers c ON c.customer_id = t.customer_id
LEFT JOIN fact_events e ON e.customer_id::int = c.customer_id
GROUP BY c.customer_id, c.full_name, t.purchase_count
ORDER BY t.purchase_count DESC;


-- Пользователи без заказов
SELECT
    c.*
FROM dim_customers c
LEFT JOIN fact_orders o ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL
ORDER BY c.created_at DESC;