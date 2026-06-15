"""Quick DB check — uses DATABASE_URL from env."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sqlalchemy import text

from models import engine

with engine.connect() as conn:
    games = conn.execute(text("SELECT COUNT(*) FROM games")).scalar()
    scans = conn.execute(text("SELECT COUNT(*) FROM scans")).scalar()
    host = conn.execute(text("SELECT inet_server_addr()")).scalar()
print(f"games={games} scans={scans} server={host}")
