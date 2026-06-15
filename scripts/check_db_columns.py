"""Check scans table columns on configured database."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

url = os.getenv("RENDER_DATABASE_URL") or os.getenv("DATABASE_URL")
if not url:
    print("NO_URL", file=sys.stderr)
    sys.exit(1)

if "render.com" in url and "sslmode=" not in url:
    url += "&sslmode=require" if "?" in url else "?sslmode=require"

import psycopg2

conn = psycopg2.connect(url)
cur = conn.cursor()
cur.execute(
    "SELECT column_name FROM information_schema.columns "
    "WHERE table_name='scans' ORDER BY 1"
)
print("columns:", [r[0] for r in cur.fetchall()])
conn.close()
