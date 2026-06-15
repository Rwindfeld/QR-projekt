"""Idempotent database migrations (Render + local)."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Engine

_MIGRATION_STATEMENTS = [
    "ALTER TABLE scans ADD COLUMN IF NOT EXISTS visitor_token VARCHAR(36)",
    "ALTER TABLE scans ADD COLUMN IF NOT EXISTS discount_eligible BOOLEAN DEFAULT FALSE",
    "ALTER TABLE scans ADD COLUMN IF NOT EXISTS discount_pct SMALLINT DEFAULT 0",
    "UPDATE scans SET discount_eligible = FALSE WHERE discount_eligible IS NULL",
    "UPDATE scans SET discount_pct = 0 WHERE discount_pct IS NULL",
    "ALTER TABLE scans ALTER COLUMN discount_eligible SET DEFAULT FALSE",
    "ALTER TABLE scans ALTER COLUMN discount_eligible SET NOT NULL",
    "ALTER TABLE scans ALTER COLUMN discount_pct SET DEFAULT 0",
    "ALTER TABLE scans ALTER COLUMN discount_pct SET NOT NULL",
    (
        "CREATE INDEX IF NOT EXISTS idx_scans_visitor_day "
        "ON scans (visitor_token, scanned_at DESC) "
        "WHERE visitor_token IS NOT NULL"
    ),
    (
        "CREATE INDEX IF NOT EXISTS idx_scans_visitor_game_time "
        "ON scans (visitor_token, game_id, scanned_at DESC) "
        "WHERE visitor_token IS NOT NULL"
    ),
]


def run_migrations(engine: Engine) -> None:
    """Apply schema updates; safe to call on every startup and before scans."""
    with engine.begin() as conn:
        for stmt in _MIGRATION_STATEMENTS:
            conn.execute(text(stmt))
