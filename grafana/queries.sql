-- Grafana Postgres — café-ejer: efterspørgsel ved hylden (ingen bord-data)
-- Bruger dashboardets tidsvælger: $__timeFilter / $__timeGroupAlias

-- KPI: Scanninger i perioden
SELECT COUNT(*)::bigint AS value FROM scans WHERE $__timeFilter(scanned_at);

-- KPI: Spil med mindst 1 scan
SELECT COUNT(DISTINCT s.game_id)::bigint AS value FROM scans s WHERE $__timeFilter(s.scanned_at);

-- KPI: Andel af kataloget i brug (%)
SELECT ROUND(100.0 * COUNT(DISTINCT s.game_id) / NULLIF((SELECT COUNT(*)::numeric FROM games), 0), 1) AS value
FROM scans s WHERE $__timeFilter(s.scanned_at);

-- KPI: Spil med lave scanninger (bruger variabel ${max_lav_scans}: 5, 10, 15 eller 20)
SELECT COUNT(*)::bigint AS value FROM games g
LEFT JOIN (
  SELECT s.game_id, COUNT(*)::bigint AS scans FROM scans s
  WHERE $__timeFilter(s.scanned_at) GROUP BY s.game_id
) cnt ON cnt.game_id = g.id
WHERE COALESCE(cnt.scans, 0) <= ${max_lav_scans};

-- Top 15 efterspørgsel (slug bruges til klik-link i Grafana, skjules i diagram)
SELECT g.name AS name, g.slug AS slug, COUNT(*)::bigint AS scans
FROM scans s JOIN games g ON g.id = s.game_id
WHERE $__timeFilter(s.scanned_at)
GROUP BY g.id, g.name, g.slug ORDER BY scans DESC LIMIT 15;

-- Trend: scanninger pr. dag
SELECT $__timeGroupAlias(scanned_at,'1d'), COUNT(*)::bigint AS value
FROM scans WHERE $__timeFilter(scanned_at) GROUP BY 1 ORDER BY 1;

-- Tabel: spil med lave scanninger (0 .. ${max_lav_scans} i perioden)
SELECT g.name AS "Spil", g.slug AS "Slug", COALESCE(g.year_published::text, '—') AS "År",
  COALESCE(cnt.scans, 0)::bigint AS "Scanninger"
FROM games g
LEFT JOIN (
  SELECT s.game_id, COUNT(*)::bigint AS scans FROM scans s
  WHERE $__timeFilter(s.scanned_at) GROUP BY s.game_id
) cnt ON cnt.game_id = g.id
WHERE COALESCE(cnt.scans, 0) <= ${max_lav_scans}
ORDER BY COALESCE(cnt.scans, 0) ASC, g.name;

-- Seneste 50 scanninger (klik på Slug -> QR-side)
SELECT s.scanned_at AS "Tidspunkt", g.name AS "Spil", g.slug AS "Slug"
FROM scans s JOIN games g ON g.id = s.game_id
WHERE $__timeFilter(s.scanned_at) ORDER BY s.scanned_at DESC LIMIT 50;

-- Bar: scanninger per ugedag (kun name + scans — som Top 15-panelet)
WITH t AS (
  SELECT EXTRACT(ISODOW FROM scanned_at AT TIME ZONE 'Europe/Copenhagen')::int AS dow
  FROM scans WHERE $__timeFilter(scanned_at)
)
SELECT CASE dow
  WHEN 1 THEN 'Mandag' WHEN 2 THEN 'Tirsdag' WHEN 3 THEN 'Onsdag' WHEN 4 THEN 'Torsdag'
  WHEN 5 THEN 'Fredag' WHEN 6 THEN 'Loerdag' WHEN 7 THEN 'Soendag' END AS name,
  COUNT(*)::bigint AS scans
FROM t GROUP BY dow ORDER BY dow;

-- Bar: scanninger per tidsrum (kun name + scans)
WITH t AS (
  SELECT EXTRACT(HOUR FROM scanned_at AT TIME ZONE 'Europe/Copenhagen')::int AS h
  FROM scans WHERE $__timeFilter(scanned_at)
), b AS (
  SELECT
    CASE WHEN h BETWEEN 10 AND 13 THEN 1 WHEN h BETWEEN 14 AND 16 THEN 2
         WHEN h BETWEEN 17 AND 21 THEN 3 WHEN h < 10 THEN 4 ELSE 5 END AS s,
    CASE WHEN h BETWEEN 10 AND 13 THEN '10-14 Formiddag' WHEN h BETWEEN 14 AND 16 THEN '14-17 Eftermiddag'
         WHEN h BETWEEN 17 AND 21 THEN '17-22 Aften' WHEN h < 10 THEN 'Foer aabning'
         ELSE 'Sent / andet' END AS name
  FROM t
)
SELECT name, COUNT(*)::bigint AS scans FROM b GROUP BY s, name ORDER BY s;

-- Ydeevne: gns. tider (ms)
SELECT ROUND(AVG(server_duration_ms))::bigint FROM scans
WHERE $__timeFilter(scanned_at) AND server_duration_ms IS NOT NULL;

SELECT ROUND(AVG(db_duration_ms))::bigint FROM scans
WHERE $__timeFilter(scanned_at) AND db_duration_ms IS NOT NULL;

SELECT ROUND(AVG(client_load_ms))::bigint FROM scans
WHERE $__timeFilter(scanned_at) AND client_load_ms IS NOT NULL;

-- Seneste scans med timing
SELECT s.scanned_at, g.name, s.server_duration_ms, s.db_duration_ms, s.client_load_ms
FROM scans s JOIN games g ON g.id = s.game_id
WHERE $__timeFilter(s.scanned_at) ORDER BY s.scanned_at DESC LIMIT 30;
