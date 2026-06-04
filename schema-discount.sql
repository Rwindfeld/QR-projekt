-- Drikkevarerabat ved scanning (besøgs-token + om rabat tæller)
ALTER TABLE scans ADD COLUMN IF NOT EXISTS visitor_token VARCHAR(36);
ALTER TABLE scans ADD COLUMN IF NOT EXISTS discount_eligible BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE scans ADD COLUMN IF NOT EXISTS discount_pct SMALLINT NOT NULL DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_scans_visitor_day
    ON scans (visitor_token, scanned_at DESC)
    WHERE visitor_token IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_scans_visitor_game_time
    ON scans (visitor_token, game_id, scanned_at DESC)
    WHERE visitor_token IS NOT NULL;
