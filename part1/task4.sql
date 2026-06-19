--Задача 4: Динамика прослушиваний по месяцам
--Составь таблицу с суммарным количеством прослушиваний по месяцам для всех песен.
--Формат вывода: year_month (ТЕХТ, формат УУУУ-ММ), total_listens (INTEGER)

SELECT 
	STRFTIME('%Y-%m', listen_time) AS year_month,
	COUNT(*) AS total_listens
FROM listening_logs
GROUP BY year_month
ORDER BY year_month;
