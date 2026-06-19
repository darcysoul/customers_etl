--Задача 3: Альбом с самой крутой коллаборацией
--Найди альбом, в котором больше всего песен с *несколькими* артистами. 
--В ответе покажи название альбома, основного исполнителя и количество совместных песен.
--Формат вывода: album (TEXT), artist (TEXT), collab_count (INTEGER)

WITH collab_songs AS (
    -- песни, у которых больше одного артиста
    SELECT
        song_id,
        COUNT(*) AS artist_count
    FROM song_artists
    GROUP BY song_id
    HAVING COUNT(*) > 1
)
SELECT
    a.title AS album,
    ar.name AS artist,
    COUNT(*) AS collab_count
FROM collab_songs cs
JOIN songs s ON s.song_id = cs.song_id
JOIN albums a ON a.album_id = s.album_id
JOIN artists ar ON a.artist_id = ar.artist_id
GROUP BY a.album_id, a.title, ar.artist_id, ar.name
ORDER BY collab_count DESC
LIMIT 1;
