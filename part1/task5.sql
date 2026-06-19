--Задача 5: Популярность жанров по регионам
--Составь сводную таблицу с суммарным количеством прослушиваний по жанрам и регионам.
--Формат вывода: genre (TEXT), region (TEXT), total_listens (INTEGER)

SELECT
	g.name AS genre,
	ll.region AS region,
	COUNT(*) total_listens
FROM listening_logs ll 
JOIN songs s ON s.song_id=ll.song_id 
JOIN song_genres sg ON sg.song_id=s.song_id
JOIN genres g ON g.genre_id=sg.genre_id
GROUP BY g.genre_id, g.name, ll.region
ORDER BY total_listens DESC;
