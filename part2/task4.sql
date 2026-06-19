-- Задача 4.
-- Симметричные пары:
-- Условие: Даны таблица items (id, name, category).
-- Задание: Найти все пары записей, у которых полностью совпадают 
-- name и category. Пары (id1,id2) и (id2, id1) считай идентичными 
-- (оставь только одну). 
-- Пары с одинаковыми ID необходимо исключить.
-- Ожидаемый результат: id1, id2, category.

CREATE TABLE items (id INTEGER, name TEXT, category TEXT);
INSERT INTO items VALUES
(1, 'Honor Magicbook15', 'laptop'),
(2, 'Honor Magicbook15', 'laptop'), 
(3, 'Honor Magicbook15', 'laptop'),
(4, 'Airpods 4', 'earphones'),
(5, 'Airpods 4', 'accessory');

SELECT
    i1.id AS id1,
    i2.id AS id2,
    i1.category
FROM items i1
JOIN items i2
    ON i1.name = i2.name
    AND i1.category = i2.category
    AND i1.id < i2.id
ORDER BY id1, id2;
