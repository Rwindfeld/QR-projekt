-- Render PostgreSQL — tables only (no PgBouncer admin user)

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
    id              BIGSERIAL PRIMARY KEY,
    game_id         INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    scanned_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    table_location  VARCHAR(32),
    user_agent      TEXT,
    ip_hash         CHAR(64)
);

CREATE INDEX IF NOT EXISTS idx_scans_scanned_at ON scans (scanned_at DESC);
CREATE INDEX IF NOT EXISTS idx_scans_game_id ON scans (game_id);
CREATE INDEX IF NOT EXISTS idx_scans_game_scanned_at ON scans (game_id, scanned_at DESC);
