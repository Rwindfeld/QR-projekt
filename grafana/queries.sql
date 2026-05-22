-- Grafana Postgres panels — bruger dashboardets tidsvælger via $__timeFilter / $__timeGroupAlias
-- Vælg interval øverst (fx Last 7 days, Last 6 months) — alle paneler følger med

-- Panel: Scanninger i perioden
SELECT COUNT(*)::bigint AS value FROM scans WHERE $__timeFilter(scanned_at);

-- Panel: Forskellige spil i perioden
SELECT COUNT(DISTINCT s.game_id)::bigint AS value FROM scans s WHERE $__timeFilter(s.scanned_at);

-- Panel: Top 10 spil i perioden
SELECT g.name AS name, COUNT(*)::bigint AS scans
FROM scans s JOIN games g ON g.id = s.game_id
WHERE $__timeFilter(s.scanned_at)
GROUP BY g.id, g.name ORDER BY scans DESC LIMIT 10;

-- Panel: Scanninger pr. time
WITH top5 AS (
  SELECT s.game_id FROM scans s WHERE $__timeFilter(s.scanned_at)
  GROUP BY s.game_id ORDER BY COUNT(*) DESC LIMIT 5
)
SELECT $__timeGroupAlias(s.scanned_at,'1h'), g.name AS metric, COUNT(*)::bigint AS value
FROM scans s JOIN games g ON g.id = s.game_id
WHERE $__timeFilter(s.scanned_at) AND s.game_id IN (SELECT game_id FROM top5)
GROUP BY 1, 2 ORDER BY 1;

-- Panel: Scanninger pr. dag
SELECT $__timeGroupAlias(scanned_at,'1d'), COUNT(*)::bigint AS value
FROM scans WHERE $__timeFilter(scanned_at) GROUP BY 1 ORDER BY 1;

-- Panel: Spilfordeling i perioden
SELECT g.name AS metric, COUNT(*)::bigint AS value
FROM scans s JOIN games g ON g.id = s.game_id
WHERE $__timeFilter(s.scanned_at) GROUP BY g.id, g.name ORDER BY value DESC;

-- Panel: Seneste 50 scanninger i perioden
SELECT s.scanned_at AS "Tidspunkt", g.name AS "Spil",
  COALESCE(s.table_location, '—') AS "Bord",
  LEFT(COALESCE(s.user_agent, '—'), 48) AS "User-Agent"
FROM scans s JOIN games g ON g.id = s.game_id
WHERE $__timeFilter(s.scanned_at) ORDER BY s.scanned_at DESC LIMIT 50;

-- Panel: Aktivitet time × ugedag
SELECT
  EXTRACT(HOUR FROM scanned_at AT TIME ZONE 'Europe/Copenhagen')::int AS hour,
  TRIM(TO_CHAR(scanned_at AT TIME ZONE 'Europe/Copenhagen', 'Day')) AS weekday,
  COUNT(*)::bigint AS scans
FROM scans WHERE $__timeFilter(scanned_at) GROUP BY 1, 2;
