"""
Database bootstrap for Render (and any deploy without preDeployCommand).
Creates tables and seeds games if the database is empty.
"""
from __future__ import annotations

import os
from pathlib import Path

import psycopg2

from db_migrate import run_migrations
from models import engine
from wiki_urls import WIKIPEDIA_BY_SLUG

ROOT = Path(__file__).resolve().parent.parent


def bootstrap() -> None:
    """Idempotent: safe to run on every app startup."""
    from models import _normalize_database_url

    raw = os.environ.get("DATABASE_URL") or os.environ.get("RENDER_DATABASE_URL")
    if not raw:
        return

    raw = _normalize_database_url(raw)

    conn = psycopg2.connect(raw)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute((ROOT / "schema-render.sql").read_text(encoding="utf-8"))
    cur.execute((ROOT / "schema-timing.sql").read_text(encoding="utf-8"))
    conn.close()

    run_migrations(engine)

    conn = psycopg2.connect(raw)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM games")
    game_count = cur.fetchone()[0]
    if game_count < 50:
        cur.execute((ROOT / "seed.sql").read_text(encoding="utf-8"))

    cur.execute(
        "UPDATE games SET wikipedia_url = NULL "
        "WHERE wikipedia_url IS NOT NULL AND wikipedia_url LIKE '%Special:%'"
    )

    for slug, url in WIKIPEDIA_BY_SLUG.items():
        cur.execute(
            "UPDATE games SET wikipedia_url = %s WHERE slug = %s",
            (url, slug),
        )

    conn.close()


if __name__ == "__main__":
    bootstrap()
    print("Bootstrap OK")
