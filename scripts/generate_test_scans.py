"""
Generate realistic test scans for the last N months (default 6).
Does NOT delete existing scans — only INSERTs new rows.

Usage:
  python scripts/generate_test_scans.py
  python scripts/generate_test_scans.py --months 6 --count 1500

Requires DATABASE_URL or RENDER_DATABASE_URL in .env (or environment).
"""
from __future__ import annotations

import argparse
import hashlib
import os
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_batch

ROOT = Path(__file__).resolve().parent.parent

# Relative popularity in a Danish board-game café
GAME_WEIGHTS: dict[str, int] = {
    "catan": 12,
    "ticket-to-ride": 10,
    "carcassonne": 9,
    "azul": 8,
    "codenames": 8,
    "king-of-tokyo": 7,
    "wingspan": 7,
    "7-wonders": 6,
    "splendor": 6,
    "dixit": 6,
    "pandemic": 5,
    "kingdomino": 5,
    "sushi-go": 5,
    "terraforming-mars": 4,
    "everdell": 4,
    "cascadia": 4,
    "patchwork": 4,
    "exploding-kittens": 4,
    "the-quacks-of-quedlinburg": 3,
    "love-letter": 3,
    "root": 3,
    "scythe": 2,
    "klask": 3,
    "risk": 2,
    "monopoly": 2,
}

USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
]

TABLES = [f"B{i}" for i in range(1, 13)] + [f"T{i}" for i in range(1, 9)] + [None, None]


def _db_url() -> str:
    url = os.getenv("RENDER_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not url:
        raise SystemExit("Set DATABASE_URL or RENDER_DATABASE_URL in .env")
    if "render.com" in url and "sslmode=" not in url:
        url += "&sslmode=require" if "?" in url else "?sslmode=require"
    return url


def _load_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


def random_timestamp(start: datetime, end: datetime) -> datetime:
    """More scans on Fri–Sun and between 16:00–22:00 (café pattern)."""
    for _ in range(50):
        delta = end - start
        secs = random.randint(0, int(delta.total_seconds()))
        ts = start + timedelta(seconds=secs)
        # Europe/Copenhagen-ish local behaviour: use UTC+1 simplification
        local_hour = (ts.hour + 1) % 24
        weekday = ts.weekday()  # 0=Mon
        is_weekend = weekday >= 4
        is_evening = 16 <= local_hour <= 22
        weight = 1.0
        if is_weekend:
            weight *= 2.2
        if is_evening:
            weight *= 1.8
        if random.random() < min(weight / 4.0, 1.0):
            return ts
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate test scan data")
    parser.add_argument("--months", type=int, default=6, help="Months of history")
    parser.add_argument("--count", type=int, default=1200, help="Number of scans to insert")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    random.seed(args.seed)
    _load_env()
    url = _db_url()

    conn = psycopg2.connect(url)
    cur = conn.cursor()
    cur.execute("SELECT id, slug FROM games")
    rows = cur.fetchall()
    if not rows:
        raise SystemExit("No games in database — run seed.sql first")

    slug_to_id = {slug: gid for gid, slug in rows}
    weights = []
    ids = []
    for slug, gid in slug_to_id.items():
        w = GAME_WEIGHTS.get(slug, 1)
        weights.append(w)
        ids.append(gid)

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=args.months * 30)

    batch = []
    for _ in range(args.count):
        game_id = random.choices(ids, weights=weights, k=1)[0]
        ts = random_timestamp(start, end)
        table = random.choice(TABLES)
        ua = random.choice(USER_AGENTS)
        ip_hash = hashlib.sha256(f"test-{random.randint(1, 10_000_000)}".encode()).hexdigest()
        batch.append((game_id, ts, table, ua, ip_hash))

    execute_batch(
        cur,
        """
        INSERT INTO scans (game_id, scanned_at, table_location, user_agent, ip_hash)
        VALUES (%s, %s, %s, %s, %s)
        """,
        batch,
        page_size=500,
    )
    conn.commit()
    conn.close()

    print(f"OK — inserted {args.count} test scans from {start.date()} to {end.date()}")
    print("Refresh Grafana dashboard (Last 6 months or 30 days).")


if __name__ == "__main__":
    main()
