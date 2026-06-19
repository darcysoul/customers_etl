--Задача 1: Выбери самый прослушиваемый Rock-альбом
--Найди альбом, в котором суммарное количество прослушиваний песен в жанре Rock самое большое.
--Формат вывода: album (TEXT), artist (TEXT), listens (INTEGER)

SELECT 
	a.title AS album,
	ar.name AS artist,
	COUNT(*) AS listens
FROM genres g
JOIN song_genres sg  ON g.genre_id=sg.genre_id
JOIN songs s ON s.song_id=sg.song_id
JOIN albums a ON a.album_id=s.album_id
JOIN artists ar ON a.artist_id=ar.artist_id
JOIN listening_logs ll ON ll.song_id=s.song_id 
WHERE g.name='Rock'
GROUP BY a.album_id, a.title, ar.artist_id, ar.name
ORDER BY listens DESC
LIMIT 1;