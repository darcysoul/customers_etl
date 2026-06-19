--Задача 2.  
--Цепочки ID:
--Условие: Даны две таблицы users(id, new_id), 
--links(id1, id2), описывающие историю изменений
--ID одного пользователя (например, 1 → 2 → 3).
--
--Используй два подхода к решению: рекурсивный и нет.
--Задание: На основе связей определи для каждого исходного ID единый 
--финальный new_id (минимальный ID в цепочке) и дедублицируй записи.
--
--Ожидаемый результат: id -> new_id
--(например, 1, 2, 3, 5 → 1; 4 → 4;7, 8 → 7).


-- cоздаём и заполняем тестовые таблицы
CREATE TABLE links (id1 INTEGER, id2 INTEGER);
INSERT INTO links VALUES
(1, 2),
(2, 3),
(5, 1);

CREATE TABLE users (id INTEGER);
INSERT INTO users VALUES (1),(2),(3),(4),(5),(7),(8);

-- нерекурсивный: до 3 уровней в глубину
WITH all_paths AS (
    SELECT id AS original_id, id AS reached_id FROM users
    UNION ALL
    SELECT u.id, l1.id2
    FROM users u JOIN links l1 ON l1.id1 = u.id
    UNION ALL
    SELECT u.id, l2.id2
    FROM users u
    JOIN links l1 ON l1.id1 = u.id
    JOIN links l2 ON l2.id1 = l1.id2
    UNION ALL
    SELECT u.id, l3.id2
    FROM users u
    JOIN links l1 ON l1.id1 = u.id
    JOIN links l2 ON l2.id1 = l1.id2
    JOIN links l3 ON l3.id1 = l2.id2
)
SELECT original_id AS id, MIN(reached_id) AS new_id
FROM all_paths
GROUP BY original_id
ORDER BY original_id;

-- рекурсивный
WITH RECURSIVE chain AS (
    SELECT id AS original_id, id AS current_id
    FROM users
    UNION ALL
    SELECT c.original_id, l.id2
    FROM chain c
    JOIN links l ON l.id1 = c.current_id
)
SELECT original_id AS id, MIN(current_id) AS new_id
FROM chain
GROUP BY original_id
ORDER BY original_id;