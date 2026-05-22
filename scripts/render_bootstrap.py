"""
Run on Render release/deploy: create tables and seed games if database is empty.
Uses DATABASE_URL from environment (Render Postgres).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg2

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    raw = os.environ.get("DATABASE_URL")
    if not raw:
        print("DATABASE_URL not set — skip bootstrap (local dev).", file=sys.stderr)
        sys.exit(0)

    if "render.com" in raw and "sslmode=" not in raw:
        raw += "&sslmode=require" if "?" in raw else "?sslmode=require"

    conn = psycopg2.connect(raw)
    conn.autocommit = True
    cur = conn.cursor()

    schema = (ROOT / "schema-render.sql").read_text(encoding="utf-8")
    cur.execute(schema)
    print("Applied schema-render.sql")

    cur.execute("SELECT COUNT(*) FROM games")
    count = cur.fetchone()[0]
    if count == 0:
        seed = (ROOT / "seed.sql").read_text(encoding="utf-8")
        cur.execute(seed)
        print("Applied seed.sql (empty database)")
    else:
        print(f"Skip seed — {count} games already present")

    conn.close()
    print("Bootstrap OK")


if __name__ == "__main__":
    main()
