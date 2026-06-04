-- QR Café Game Tracking — database schema
-- Docker: mounted as /docker-entrypoint-initdb.d/01-schema.sql (POSTGRES_DB=QR)
-- pgAdmin/local: connect to database QR on port 5432, then run this file

-- ---------------------------------------------------------------------------
-- Application tables
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS games (
    id              SERIAL PRIMARY KEY,
    slug            VARCHAR(64) NOT NULL UNIQUE,
    name            VARCHAR(128) NOT NULL,
    year_published  SMALLINT,
    awards          TEXT,
    fun_fact        TEXT NOT NULL,
    wikipedia_url   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE games ADD COLUMN IF NOT EXISTS wikipedia_url TEXT;

CREATE TABLE IF NOT EXISTS scans (
    id                  BIGSERIAL PRIMARY KEY,
    game_id             INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    scanned_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    table_location      VARCHAR(32),
    user_agent          TEXT,
    ip_hash             CHAR(64),
    server_duration_ms  INTEGER,
    db_duration_ms      INTEGER,
    client_load_ms      INTEGER
);

ALTER TABLE scans ADD COLUMN IF NOT EXISTS server_duration_ms INTEGER;
ALTER TABLE scans ADD COLUMN IF NOT EXISTS db_duration_ms INTEGER;
ALTER TABLE scans ADD COLUMN IF NOT EXISTS client_load_ms INTEGER;
ALTER TABLE scans ADD COLUMN IF NOT EXISTS visitor_token VARCHAR(36);
ALTER TABLE scans ADD COLUMN IF NOT EXISTS discount_eligible BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE scans ADD COLUMN IF NOT EXISTS discount_pct SMALLINT NOT NULL DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_scans_scanned_at ON scans (scanned_at DESC);
CREATE INDEX IF NOT EXISTS idx_scans_game_id ON scans (game_id);
CREATE INDEX IF NOT EXISTS idx_scans_game_scanned_at ON scans (game_id, scanned_at DESC);

-- ---------------------------------------------------------------------------
-- PgBouncer stats user (Grafana Alloy scrapes admin DB "pgbouncer" on port 6432)
-- Password must match pgbouncer/userlist.txt
-- ---------------------------------------------------------------------------

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'pgbouncer_stats') THEN
        CREATE USER pgbouncer_stats WITH PASSWORD 'pgbouncer_stats_secret';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE "QR" TO pgbouncer_stats;
