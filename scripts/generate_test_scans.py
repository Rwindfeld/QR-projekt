"""
Generate realistic test scans for the last N months (default 6).
Does NOT delete existing scans — only INSERTs new rows.

Default: 1000 scans, kl. 12:00–23:00 (Europe/Copenhagen), forskellige spil og antal.

Usage:
  python scripts/generate_test_scans.py
  python scripts/generate_test_scans.py --months 6 --count 1000
  python scripts/generate_test_scans.py --count 1000 --hour-start 12 --hour-end 23

Requires DATABASE_URL or RENDER_DATABASE_URL in .env (or environment).
"""
from __future__ import annotations

import argparse
import hashlib
import os
import random
import sys
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import psycopg2
from psycopg2.extras import execute_batch

ROOT = Path(__file__).resolve().parent.parent
TZ = ZoneInfo("Europe/Copenhagen")


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

# Lidt flere scans fredag–søndag, men alle ugedage dækket
WEEKDAY_WEIGHTS = [1.0, 0.9, 0.95, 1.0, 1.15, 1.35, 1.25]  # man–søn


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


def _local_to_utc(dt_local: datetime) -> datetime:
    if dt_local.tzinfo is None:
        dt_local = dt_local.replace(tzinfo=TZ)
    return dt_local.astimezone(timezone.utc)


def random_cafe_timestamp(
    start_local: datetime,
    end_local: datetime,
    hour_start: int,
    hour_end: int,
) -> datetime:
    """Tilfældigt tidspunkt på en tilfældig dag, kl. hour_start–hour_end (København)."""
    start_date = start_local.date()
    end_date = end_local.date()
    day_span = (end_date - start_date).days
    if day_span < 0:
        day_span = 0

    for _ in range(80):
        day_offset = random.randint(0, day_span)
        day = start_date + timedelta(days=day_offset)
        weekday = day.weekday()
        if random.random() > min(WEEKDAY_WEIGHTS[weekday] / 1.35, 1.0):
            continue

        hour = random.randint(hour_start, hour_end - 1) if hour_end > hour_start else hour_start
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        dt_local = datetime.combine(day, time(hour, minute, second), tzinfo=TZ)

        if dt_local < start_local or dt_local > end_local:
            continue
        return _local_to_utc(dt_local)

    # Fallback
    day = start_date + timedelta(days=random.randint(0, max(day_span, 0)))
    hour = random.randint(hour_start, max(hour_start, hour_end - 1))
    return _local_to_utc(datetime.combine(day, time(hour, random.randint(0, 59)), tzinfo=TZ))


def _allocate_scan_counts(
    game_ids: list[int],
    game_weights: list[int],
    total: int,
    min_games: int,
) -> dict[int, int]:
    """Fordel total scans på mange spil — nogle få populære, mange med få."""
    if not game_ids:
        return {}

    n_active = min(len(game_ids), max(min_games, total // 3))
    active_indices = random.sample(range(len(game_ids)), n_active)
    active_ids = [game_ids[i] for i in active_indices]
    active_weights = [game_weights[i] for i in active_indices]

    # Zipf-lignende: vægtet tilfældig fordeling giver spredte antal
    counts: dict[int, int] = {gid: 0 for gid in active_ids}
    for _ in range(total):
        gid = random.choices(active_ids, weights=active_weights, k=1)[0]
        counts[gid] += 1

    # Fjern spil der tilfældigt fik 0 (skulle ikke ske)
    return {gid: c for gid, c in counts.items() if c > 0}


def _ensure_weekday_coverage(
    counts: dict[int, int],
    game_ids: list[int],
    start_local: datetime,
    end_local: datetime,
    hour_start: int,
    hour_end: int,
) -> list[tuple[int, datetime]]:
    """Mindst ét scan pr. ugedag (man–søn) spredt i perioden."""
    extra: list[tuple[int, datetime]] = []
    if not game_ids:
        return extra

    day_span = max((end_local.date() - start_local.date()).days, 6)
    for weekday in range(7):
        offset = int(day_span * (weekday + 1) / 8)
        day = start_local.date() + timedelta(days=offset)
        while day.weekday() != weekday and day <= end_local.date():
            day += timedelta(days=1)
        if day > end_local.date():
            day = end_local.date() - timedelta(days=(end_local.date().weekday() - weekday) % 7)

        hour = hour_start + (weekday * 2) % max(1, hour_end - hour_start)
        minute = (weekday * 11) % 60
        dt_local = datetime.combine(day, time(hour, minute, 0), tzinfo=TZ)
        if dt_local < start_local:
            dt_local = start_local
        if dt_local > end_local:
            dt_local = end_local - timedelta(hours=1)
        extra.append((random.choice(game_ids), _local_to_utc(dt_local)))
    return extra


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate test scan data")
    parser.add_argument("--months", type=int, default=6, help="Months of history")
    parser.add_argument("--count", type=int, default=1000, help="Number of scans to insert")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--hour-start", type=int, default=12, help="Earliest hour (local, inclusive)")
    parser.add_argument("--hour-end", type=int, default=23, help="Latest hour (local, exclusive end = 22:59)")
    parser.add_argument(
        "--min-games",
        type=int,
        default=120,
        help="Minimum number of different games that receive scans",
    )
    parser.add_argument(
        "--bulk-active-fraction",
        type=float,
        default=0.18,
        help="Share of bulk games eligible for scans",
    )
    parser.add_argument(
        "--core-scan-share",
        type=float,
        default=0.35,
        help="Weight bias toward 100 core café hits in allocation",
    )
    args = parser.parse_args()

    if args.hour_start < 0 or args.hour_end > 24 or args.hour_start >= args.hour_end:
        raise SystemExit("hour-start skal være mindre end hour-end (fx 12 og 23)")

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
            core_weights.append(max(1, int(w * (1 + args.core_scan_share * 3))))
        else:
            bulk_ids.append(gid)
            bulk_weights.append(w)

    bulk_active_n = max(1, int(len(bulk_ids) * args.bulk_active_fraction))
    bulk_active_indices = random.sample(range(len(bulk_ids)), min(bulk_active_n, len(bulk_ids)))
    bulk_active_ids = [bulk_ids[i] for i in bulk_active_indices]
    bulk_active_weights = [bulk_weights[i] for i in bulk_active_indices]

    pool_ids = core_ids + bulk_active_ids
    pool_weights = core_weights + bulk_active_weights

    end_local = datetime.now(TZ)
    start_local = end_local - timedelta(days=args.months * 30)

    counts = _allocate_scan_counts(
        pool_ids,
        pool_weights,
        args.count,
        min(args.min_games, len(pool_ids)),
    )

    batch: list[tuple] = []
    for game_id, n in counts.items():
        for _ in range(n):
            ts = random_cafe_timestamp(
                start_local, end_local, args.hour_start, args.hour_end
            )
            ua = random.choice(USER_AGENTS)
            ip_hash = hashlib.sha256(
                f"test-{game_id}-{random.randint(1, 10_000_000)}".encode()
            ).hexdigest()
            db_ms = random.randint(15, 120)
            server_ms = db_ms + random.randint(30, 350)
            client_ms = random.randint(400, 4500)
            if random.random() < 0.08:
                client_ms = None
            batch.append((game_id, ts, ua, ip_hash, server_ms, db_ms, client_ms))

    # Ugedags-dækning (7 ekstra, stadig inden for åbningstid)
    for game_id, ts in _ensure_weekday_coverage(
        counts, pool_ids, start_local, end_local, args.hour_start, args.hour_end
    ):
        batch.append(
            (
                game_id,
                ts,
                random.choice(USER_AGENTS),
                hashlib.sha256(f"weekday-{ts.isoformat()}".encode()).hexdigest(),
                random.randint(40, 200),
                random.randint(20, 90),
                random.randint(500, 3000),
            )
        )

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

    cur.execute("SELECT COUNT(*) FROM scans")
    total_scans = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT game_id) FROM scans")
    games_used = cur.fetchone()[0]
    cur.execute(
        """
        SELECT EXTRACT(DOW FROM scanned_at AT TIME ZONE 'Europe/Copenhagen')::int AS dow,
               COUNT(*)::int
        FROM scans
        GROUP BY 1 ORDER BY 1
        """
    )
    by_dow = cur.fetchall()
    cur.execute(
        """
        SELECT EXTRACT(HOUR FROM scanned_at AT TIME ZONE 'Europe/Copenhagen')::int AS h,
               COUNT(*)::int
        FROM scans
        GROUP BY 1 ORDER BY 1
        """
    )
    by_hour = cur.fetchall()
    conn.close()

    inserted = len(batch)
    print(f"OK - indsat {inserted} test-scans ({start_local.date()} -> {end_local.date()})")
    print(f"Abningstid: kl. {args.hour_start}:00-{args.hour_end - 1}:59 (Europe/Copenhagen)")
    print(f"Katalog: {len(rows)} spil | Scans i alt nu: {total_scans} | Spil med scans: {games_used}")
    print(f"Ugedage (0=søn): {dict(by_dow)}")
    print(f"Timer: {dict(by_hour)}")
    print("Opdater Grafana: Last 6 months, refresh 30s.")


if __name__ == "__main__":
    main()
