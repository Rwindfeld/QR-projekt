"""
Generate realistic test scans for the last N months (default 6).
Does NOT delete existing scans — only INSERTs new rows.

Most of the catalog stays at 0 scans; a minority gets few/many scans (café-realistic).

Usage:
  python scripts/generate_test_scans.py
  python scripts/generate_test_scans.py --months 6 --count 15000

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


def _catalog() -> tuple[list[dict], set[str]]:
    sys.path.insert(0, str(ROOT / "scripts"))
    from games_catalog import GAMES  # noqa: E402

    try:
        from games_catalog_bulk import GAMES_BULK  # noqa: E402
    except ImportError:
        GAMES_BULK = []
    core_slugs = {g["slug"] for g in GAMES}
    return GAMES + GAMES_BULK, core_slugs


def _game_weights() -> dict[str, int]:
    games, _ = _catalog()
    return {g["slug"]: g.get("weight", 1) for g in games}


USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
]


def _db_url() -> str:
    url = os.getenv("RENDER_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not url:
        raise SystemExit("Set RENDER_DATABASE_URL in .env (Grafana bruger Render Postgres)")
    if "localhost" in url and not os.getenv("RENDER_DATABASE_URL"):
        print("ADVARSEL: Bruger localhost — Grafana ser Render. Tilføj RENDER_DATABASE_URL i .env.")
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
        local_hour = (ts.hour + 1) % 24
        weekday = ts.weekday()
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


def _pick_game_id(
    core_ids: list[int],
    core_weights: list[int],
    bulk_active_ids: list[int],
    bulk_active_weights: list[int],
    core_scan_share: float,
) -> int:
    if bulk_active_ids and random.random() < core_scan_share and core_ids:
        return random.choices(core_ids, weights=core_weights, k=1)[0]
    if bulk_active_ids:
        return random.choices(bulk_active_ids, weights=bulk_active_weights, k=1)[0]
    return random.choices(core_ids, weights=core_weights, k=1)[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate test scan data")
    parser.add_argument("--months", type=int, default=6, help="Months of history")
    parser.add_argument("--count", type=int, default=15000, help="Number of scans to insert")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument(
        "--bulk-active-fraction",
        type=float,
        default=0.16,
        help="Share of bulk (500+) games that get any scans (rest stay at 0)",
    )
    parser.add_argument(
        "--core-scan-share",
        type=float,
        default=0.22,
        help="Fraction of scans assigned to the 100 core café hits",
    )
    parser.add_argument(
        "--sparse-games",
        type=int,
        default=0,
        help="Add 1-3 scans each to N random games that still have zero scans",
    )
    args = parser.parse_args()

    random.seed(args.seed)
    _load_env()
    weights_map = _game_weights()
    _, core_slugs = _catalog()

    url = _db_url()
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    cur.execute("SELECT id, slug FROM games")
    rows = cur.fetchall()
    if not rows:
        raise SystemExit("No games in database — run seed.sql first")

    core_ids: list[int] = []
    core_weights: list[int] = []
    bulk_ids: list[int] = []
    bulk_weights: list[int] = []

    for gid, slug in rows:
        w = weights_map.get(slug, 1)
        if slug in core_slugs:
            core_ids.append(gid)
            core_weights.append(w)
        else:
            bulk_ids.append(gid)
            bulk_weights.append(w)

    bulk_active_n = max(1, int(len(bulk_ids) * args.bulk_active_fraction))
    bulk_active_indices = random.sample(range(len(bulk_ids)), min(bulk_active_n, len(bulk_ids)))
    bulk_active_ids = [bulk_ids[i] for i in bulk_active_indices]
    bulk_active_weights = [bulk_weights[i] for i in bulk_active_indices]

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=args.months * 30)

    batch = []
    for _ in range(args.count):
        game_id = _pick_game_id(
            core_ids,
            core_weights,
            bulk_active_ids,
            bulk_active_weights,
            args.core_scan_share,
        )
        ts = random_timestamp(start, end)
        ua = random.choice(USER_AGENTS)
        ip_hash = hashlib.sha256(f"test-{random.randint(1, 10_000_000)}".encode()).hexdigest()
        db_ms = random.randint(15, 120)
        server_ms = db_ms + random.randint(30, 350)
        client_ms = random.randint(400, 4500)
        if random.random() < 0.08:
            client_ms = None
        batch.append((game_id, ts, ua, ip_hash, server_ms, db_ms, client_ms))

    execute_batch(
        cur,
        """
        INSERT INTO scans (game_id, scanned_at, user_agent, ip_hash, server_duration_ms, db_duration_ms, client_load_ms)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        batch,
        page_size=500,
    )
    conn.commit()

    sparse_added = 0
    if args.sparse_games > 0:
        cur.execute(
            "SELECT g.id FROM games g WHERE NOT EXISTS (SELECT 1 FROM scans s WHERE s.game_id = g.id)"
        )
        zero_ids = [r[0] for r in cur.fetchall()]
        pick = random.sample(zero_ids, min(args.sparse_games, len(zero_ids)))
        sparse_batch = []
        for gid in pick:
            for _ in range(random.choice([1, 1, 1, 2, 2, 3])):
                db_ms = random.randint(20, 90)
                server_ms = db_ms + random.randint(40, 280)
                client_ms = random.randint(500, 3000)
                sparse_batch.append(
                    (
                        gid,
                        random_timestamp(start, end),
                        "Mozilla/5.0 (test-sparse)",
                        hashlib.sha256(f"sparse-{random.random()}".encode()).hexdigest(),
                        server_ms,
                        db_ms,
                        client_ms,
                    )
                )
        execute_batch(
            cur,
            "INSERT INTO scans (game_id, scanned_at, user_agent, ip_hash, server_duration_ms, db_duration_ms, client_load_ms) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            sparse_batch,
            page_size=200,
        )
        conn.commit()
        sparse_added = len(sparse_batch)

    cur.execute(
        """
        SELECT
          COUNT(DISTINCT game_id) FILTER (WHERE game_id = ANY(%s)) AS core_used,
          COUNT(DISTINCT game_id) FILTER (WHERE game_id = ANY(%s)) AS bulk_used,
          (SELECT COUNT(*) FROM games) AS total_games
        FROM scans
        """,
        (core_ids, bulk_ids),
    )
    core_used, bulk_used, total_games = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM scans")
    total_scans = cur.fetchone()[0]
    conn.close()

    bulk_never = len(bulk_ids) - bulk_used
    print(f"OK - inserted {args.count} test scans ({start.date()} -> {end.date()})")
    if sparse_added:
        print(f"Sparse: +{sparse_added} scans on {args.sparse_games} previously unused titles")
    print(f"Katalog: {total_games} spil | Scans i alt: {total_scans}")
    print(
        f"Bulk: {bulk_used}/{len(bulk_ids)} titler har mindst 1 scan "
        f"({bulk_never} bulk-spil stadig uden scan)"
    )
    print(f"Core: {core_used}/{len(core_ids)} kuraterede spil har mindst 1 scan")
    print("Refresh Grafana dashboard (Last 6 months).")


if __name__ == "__main__":
    main()
