--Задача 2: Кто в топ-20% по хитам
--Определи исполнителя, у которого больше всего песен в *топ-20%* по количеству прослушиваний.
--Формат вывода: artist (TEXT), top_songs (INTEGER)
--!Важно 20% - жто не топ 20

WITH song_listens AS (
	-- считаем прослушивания по каждой песне
    SELECT
        s.song_id,
        ar.name AS artist,
        ar.artist_id,
        COUNT(*) AS listens
    FROM songs s
    JOIN albums a ON a.album_id = s.album_id
    JOIN artists ar ON a.artist_id = ar.artist_id
    JOIN listening_logs ll ON ll.song_id = s.song_id
    GROUP BY s.song_id, ar.artist_id, ar.name
),
ranked AS (
	-- ранжируем все песни по прослушиваниям 
	-- в порядке убывания, разделяя их на 5 групп (в каждой по 20%)
    SELECT
    	artist_id,
        artist,
        NTILE(5) OVER (ORDER BY listens DESC) AS quintile5
    FROM song_listens
)
SELECT
    artist,
    COUNT(*) AS top_songs
FROM ranked
WHERE quintile5 = 1
GROUP BY artist_id, artist
ORDER BY top_songs DESC
LIMIT 1;