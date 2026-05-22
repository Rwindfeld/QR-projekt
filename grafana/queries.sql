-- Grafana Cloud Postgres panels — copy into panel SQL editor
-- Data source: your Grafana Cloud Postgres (via cloudflared tunnel or PDC)
-- Database: QR

-- ---------------------------------------------------------------------------
-- Panel 1: Stat — "Scanninger i dag"
-- ---------------------------------------------------------------------------
SELECT COUNT(*)::bigint AS value
FROM scans
WHERE scanned_at >= date_trunc('day', NOW() AT TIME ZONE 'Europe/Copenhagen');

-- ---------------------------------------------------------------------------
-- Panel 2: Stat — "Scanninger denne uge" (ISO week, Copenhagen TZ)
-- ---------------------------------------------------------------------------
SELECT COUNT(*)::bigint AS value
FROM scans
WHERE scanned_at >= date_trunc('week', NOW() AT TIME ZONE 'Europe/Copenhagen');

-- ---------------------------------------------------------------------------
-- Panel 3: Bar chart — "Top 10 spil denne uge"
-- Format: table → Bar chart (X=name, Y=scans)
-- ---------------------------------------------------------------------------
SELECT g.name AS name, COUNT(*)::bigint AS scans
FROM scans s
JOIN games g ON g.id = s.game_id
WHERE s.scanned_at >= NOW() - INTERVAL '7 days'
GROUP BY g.id, g.name
ORDER BY scans DESC
LIMIT 10;

-- ---------------------------------------------------------------------------
-- Panel 4: Time series — "Scanninger pr. time (sidste 24t)" stacked top 5 games
-- Grafana: Format time series, Group by game name
-- ---------------------------------------------------------------------------
WITH top5 AS (
  SELECT s.game_id
  FROM scans s
  WHERE s.scanned_at >= NOW() - INTERVAL '24 hours'
  GROUP BY s.game_id
  ORDER BY COUNT(*) DESC
  LIMIT 5
)
SELECT
  date_trunc('hour', s.scanned_at AT TIME ZONE 'Europe/Copenhagen') AS time,
  g.name AS metric,
  COUNT(*)::bigint AS value
FROM scans s
JOIN games g ON g.id = s.game_id
WHERE s.scanned_at >= NOW() - INTERVAL '24 hours'
  AND s.game_id IN (SELECT game_id FROM top5)
GROUP BY 1, 2
ORDER BY 1;

-- ---------------------------------------------------------------------------
-- Panel 5: Time series — "Scanninger pr. dag (sidste 30 dage)"
-- ---------------------------------------------------------------------------
SELECT
  date_trunc('day', scanned_at AT TIME ZONE 'Europe/Copenhagen') AS time,
  COUNT(*)::bigint AS value
FROM scans
WHERE scanned_at >= NOW() - INTERVAL '30 days'
GROUP BY 1
ORDER BY 1;

-- ---------------------------------------------------------------------------
-- Panel 6: Pie chart — "Spilfordeling denne måned"
-- ---------------------------------------------------------------------------
SELECT g.name AS metric, COUNT(*)::bigint AS value
FROM scans s
JOIN games g ON g.id = s.game_id
WHERE s.scanned_at >= date_trunc('month', NOW() AT TIME ZONE 'Europe/Copenhagen')
GROUP BY g.id, g.name
ORDER BY value DESC;

-- ---------------------------------------------------------------------------
-- Panel 7: Table — "Seneste 50 scanninger"
-- ---------------------------------------------------------------------------
SELECT
  s.scanned_at AS "Tidspunkt",
  g.name AS "Spil",
  COALESCE(s.table_location, '—') AS "Bord",
  LEFT(COALESCE(s.user_agent, '—'), 48) AS "User-Agent"
FROM scans s
JOIN games g ON g.id = s.game_id
ORDER BY s.scanned_at DESC
LIMIT 50;

-- ---------------------------------------------------------------------------
-- Panel 8: Heatmap — "Aktivitet: time × ugedag"
-- Grafana heatmap: X = hour, Y = weekday label, Z = count
-- ---------------------------------------------------------------------------
SELECT
  EXTRACT(HOUR FROM scanned_at AT TIME ZONE 'Europe/Copenhagen')::int AS hour,
  TRIM(TO_CHAR(scanned_at AT TIME ZONE 'Europe/Copenhagen', 'Day')) AS weekday,
  COUNT(*)::bigint AS scans
FROM scans
WHERE scanned_at >= NOW() - INTERVAL '30 days'
GROUP BY 1, 2;
