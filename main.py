"""
QR Café Game Tracking — FastAPI prototype.
Connects via PgBouncer (port 6432). Exposes /metrics for Grafana Alloy.
"""

from __future__ import annotations

import hashlib
import re
import os
import time
import traceback
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import qrcode
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select, update

from db_migrate import run_migrations
from discount import (
    DiscountResult,
    evaluate_discount,
    set_visitor_cookie,
    visitor_token_from_request,
)
from models import Game, Scan, engine, get_db, get_game_by_slug, monthly_scan_rank, top_games
from wiki_urls import resolve_wikipedia_url
from scripts.render_bootstrap import bootstrap

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        bootstrap()
    except Exception as exc:
        print(f"DB bootstrap warning: {exc}")
        traceback.print_exc()
    yield


BASE_URL = (
    os.getenv("BASE_URL")
    or os.getenv("RENDER_EXTERNAL_URL")
    or "http://localhost:8000"
).rstrip("/")
QRCODE_DIR = Path(__file__).parent / "static" / "qrcodes"
QRCODE_DIR.mkdir(parents=True, exist_ok=True)
QRCODES_PER_PAGE = 48
QRCODES_PER_SEARCH = 24

app = FastAPI(title="QR Café Tracking", version="0.3.0", lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

scans_total = Counter(
    "scans_total",
    "Total successful QR scans logged",
    ["game"],
)
scan_errors_total = Counter(
    "scan_errors_total",
    "Scan attempts that failed (unknown slug, DB error, etc.)",
    ["reason"],
)
scan_server_duration_seconds = Histogram(
    "scan_server_duration_seconds",
    "Server time for full /scan request (DB + HTML)",
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0),
)
scan_db_duration_seconds = Histogram(
    "scan_db_duration_seconds",
    "Database time to save scan and compute rank",
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0),
)
scan_client_load_seconds = Histogram(
    "scan_client_load_seconds",
    "Browser page load time reported from thanks page",
    buckets=(0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 30.0),
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


class ScanTimingBody(BaseModel):
    client_load_ms: int = Field(ge=0, le=120_000)


@app.get("/", response_class=HTMLResponse)
def root():
    return f"""<!DOCTYPE html>
<html lang="da"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>QR Spilcafé</title>
<link rel="stylesheet" href="/static/style.css"></head>
<body><main class="container">
<h1>QR Spilcafé — tracking</h1>
<p>Appen kører. Prøv en scanning:</p>
<ul>
<li><a href="/scan/catan">Scan Catan (demo)</a></li>
<li><a href="/admin/qrcodes">Print QR-koder</a></li>
<li><a href="/healthz">Health check (JSON)</a></li>
</ul>
<p class="lead">Permanent URL til trykte QR: <strong>{BASE_URL}/scan/&lt;spil&gt;</strong></p>
</main></body></html>"""


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/healthz/db")
def healthz_db():
    """Debug: tjek at rabat-kolonner findes (fjernes evt. senere)."""
    from sqlalchemy import text

    try:
        with engine.connect() as conn:
            cols = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name='scans' ORDER BY 1"
                )
            ).fetchall()
        return {"status": "ok", "scan_columns": [c[0] for c in cols]}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


def _hash_ip(ip: Optional[str]) -> Optional[str]:
    if not ip:
        return None
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()


def _client_ip(request: Request) -> Optional[str]:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


def _record_scan(
    request: Request, slug: str
) -> tuple[Game, int, int, int, DiscountResult, bool]:
    """Insert scan; return game, rank, scan_id, db_ms, discount, set_cookie."""
    run_migrations(engine)
    db_start = time.perf_counter()
    visitor_token, set_cookie = visitor_token_from_request(request)
    with get_db() as db:
        game = get_game_by_slug(db, slug)
        if not game:
            scan_errors_total.labels(reason="unknown_slug").inc()
            raise HTTPException(status_code=404, detail="Spil ikke fundet")

        discount = evaluate_discount(db, visitor_token, game.id)
        scan = Scan(
            game_id=game.id,
            user_agent=request.headers.get("user-agent"),
            ip_hash=_hash_ip(_client_ip(request)),
            visitor_token=visitor_token,
            discount_eligible=discount.eligible,
            discount_pct=discount.earned_pct if discount.eligible else 0,
        )
        db.add(scan)
        db.flush()
        scan_id = int(scan.id)
        rank = monthly_scan_rank(db, game.id)
        db_ms = int((time.perf_counter() - db_start) * 1000)
        scan.db_duration_ms = db_ms
        scans_total.labels(game=game.slug).inc()
        db.expunge(game)
        return game, rank, scan_id, db_ms, discount, set_cookie


def _save_server_duration(scan_id: int, server_ms: int) -> None:
    with get_db() as db:
        db.execute(
            update(Scan).where(Scan.id == scan_id).values(server_duration_ms=server_ms)
        )


@app.get("/scan/{slug}")
def scan_game(request: Request, slug: str):
    t0 = time.perf_counter()
    try:
        game, rank, scan_id, db_ms, discount, set_cookie = _record_scan(request, slug)
    except HTTPException:
        raise
    except Exception:
        scan_errors_total.labels(reason="db_error").inc()
        traceback.print_exc()
        try:
            run_migrations(engine)
            game, rank, scan_id, db_ms, discount, set_cookie = _record_scan(request, slug)
        except HTTPException:
            raise
        except Exception:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail="Kunne ikke gemme scanning")

    with get_db() as db:
        top5 = top_games(db, days=7, limit=5)

    server_ms = int((time.perf_counter() - t0) * 1000)
    _save_server_duration(scan_id, server_ms)
    scan_db_duration_seconds.observe(db_ms / 1000.0)
    scan_server_duration_seconds.observe(server_ms / 1000.0)

    wiki_url = resolve_wikipedia_url(game.slug, game.wikipedia_url)
    wiki_note = " (engelsk)" if wiki_url and "en.wikipedia.org" in wiki_url else ""
    response = templates.TemplateResponse(
        request,
        "thanks.html",
        {
            "game": game,
            "rank": rank,
            "top5": top5,
            "wiki_url": wiki_url,
            "wiki_note": wiki_note,
            "scan_id": scan_id,
            "server_ms": server_ms,
            "db_ms": db_ms,
            "discount": discount,
        },
    )
    if set_cookie:
        set_visitor_cookie(response, discount.visitor_token)
    return response


@app.post("/api/scan-timing/{scan_id}")
def report_scan_timing(scan_id: int, body: ScanTimingBody):
    """Browser reports page load time after thanks.html loads."""
    with get_db() as db:
        scan = db.get(Scan, scan_id)
        if not scan:
            raise HTTPException(status_code=404, detail="Scan ikke fundet")
        scanned = scan.scanned_at
        if scanned.tzinfo is None:
            scanned = scanned.replace(tzinfo=timezone.utc)
        age_sec = (datetime.now(timezone.utc) - scanned.astimezone(timezone.utc)).total_seconds()
        if age_sec > 600:
            raise HTTPException(status_code=410, detail="Scan for gammel til timing")
        scan.client_load_ms = body.client_load_ms

    scan_client_load_seconds.observe(body.client_load_ms / 1000.0)
    return {"ok": True, "scan_id": scan_id, "client_load_ms": body.client_load_ms}


@app.get("/api/stats/top-games")
def api_top_games(days: int = 7):
    if days < 1 or days > 365:
        raise HTTPException(status_code=400, detail="days must be 1–365")
    with get_db() as db:
        rows = top_games(db, days=days, limit=10)
    return {
        "days": days,
        "games": [{"name": name, "scans": count} for name, count in rows],
    }


def _ensure_qrcode(slug: str) -> Path:
    """Lazy fallback if a new game was added after deploy build."""
    path = QRCODE_DIR / f"{slug}.png"
    if path.is_file():
        return path
    url = f"{BASE_URL}/scan/{slug}"
    img = qrcode.make(url, box_size=6, border=2)
    img.save(path, optimize=True)
    return path


@app.get("/admin/qrcodes")
def admin_qrcodes(request: Request, q: str = "", page: int = 1):
    """
    Prototype-print side:
    - Uden søgning: paginate hele kataloget.
    - Med søgning: vis kun første side af matches (ingen pagination) for at gøre det hurtigt.
    """
    q = (q or "").strip()
    page = max(1, page)

    is_search = bool(q)
    per_page = QRCODES_PER_SEARCH if is_search else QRCODES_PER_PAGE
    offset = 0 if is_search else (page - 1) * QRCODES_PER_PAGE

    where_clause = None
    if is_search:
        pat = f"%{q}%"
        where_clause = or_(Game.name.ilike(pat), Game.slug.ilike(pat))

    with get_db() as db:
        total_stmt = select(func.count()).select_from(Game)
        games_stmt = select(Game).order_by(Game.name)

        if where_clause is not None:
            total_stmt = total_stmt.where(where_clause)
            games_stmt = games_stmt.where(where_clause)

        total = db.scalar(total_stmt) or 0

        games_stmt = games_stmt.offset(offset).limit(per_page)
        games = list(db.scalars(games_stmt).all())
        for game in games:
            db.expunge(game)

    # Ingen pagination ved søgning (for hastighed)
    total_pages = 1 if is_search else max(1, (total + QRCODES_PER_PAGE - 1) // QRCODES_PER_PAGE)
    if not is_search and page > total_pages:
        page = total_pages

    return templates.TemplateResponse(
        request,
        "qrcodes.html",
        {
            "games": games,
            "base_url": BASE_URL,
            "q": q,
            "is_search": is_search,
            "page": page,
            "total_pages": total_pages,
            "total_games": total,
            "per_page": per_page,
        },
    )


@app.get("/qrcodes/{slug}.png")
def serve_qrcode(slug: str):
    if not re.fullmatch(r"[a-z0-9-]+", slug):
        raise HTTPException(status_code=400, detail="Ugyldigt spil")
    path = _ensure_qrcode(slug)
    return FileResponse(path, media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})
