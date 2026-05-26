"""
Database bootstrap for Render (and any deploy without preDeployCommand).
Creates tables and seeds games if the database is empty.
"""
from __future__ import annotations

import os
from pathlib import Path

import psycopg2

from wiki_urls import WIKIPEDIA_BY_SLUG

ROOT = Path(__file__).resolve().parent.parent


def bootstrap() -> None:
    """Idempotent: safe to run on every app startup."""
    raw = os.environ.get("DATABASE_URL")
    if not raw:
        return

    if "render.com" in raw and "sslmode=" not in raw:
        raw += "&sslmode=require" if "?" in raw else "?sslmode=require"

    conn = psycopg2.connect(raw)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute((ROOT / "schema-render.sql").read_text(encoding="utf-8"))
    cur.execute((ROOT / "schema-timing.sql").read_text(encoding="utf-8"))

    # Upsert all games (keeps existing scans)
    cur.execute((ROOT / "seed.sql").read_text(encoding="utf-8"))

    for slug, url in WIKIPEDIA_BY_SLUG.items():
        cur.execute(
            "UPDATE games SET wikipedia_url = %s WHERE slug = %s",
            (url, slug),
        )

    conn.close()


if __name__ == "__main__":
    bootstrap()
    print("Bootstrap OK")
