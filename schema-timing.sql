-- Timing columns for scan performance (Grafana + rapport)
ALTER TABLE scans ADD COLUMN IF NOT EXISTS server_duration_ms INTEGER;
ALTER TABLE scans ADD COLUMN IF NOT EXISTS db_duration_ms INTEGER;
ALTER TABLE scans ADD COLUMN IF NOT EXISTS client_load_ms INTEGER;
