"""
QR Café Game Tracking — FastAPI prototype.
Connects via PgBouncer (port 6432). Exposes /metrics for Grafana Alloy.
"""

from __future__ import annotations

import hashlib
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import qrcode
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator

from sqlalchemy import select

from models import Game, Scan, get_db, get_game_by_slug, monthly_scan_rank, top_games
from scripts.render_bootstrap import bootstrap

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Render free tier has no preDeployCommand — init DB on startup instead
    try:
        bootstrap()
    except Exception as exc:
        print(f"DB bootstrap warning: {exc}")
    yield


# Permanent QR: on Render, RENDER_EXTERNAL_URL is the stable public HTTPS URL
BASE_URL = (
    os.getenv("BASE_URL")
    or os.getenv("RENDER_EXTERNAL_URL")
    or "http://localhost:8000"
).rstrip("/")
QRCODE_DIR = Path(__file__).parent / "qrcodes"
QRCODE_DIR.mkdir(exist_ok=True)

app = FastAPI(title="QR Café Tracking", version="0.2.0", lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Custom Prometheus metrics (scraped by Alloy → Grafana Cloud)
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

Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


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
    request: Request,
    slug: str,
    table_location: Optional[str] = None,
) -> tuple[Game, int]:
    """Insert scan and return game + monthly rank."""
    with get_db() as db:
        game = get_game_by_slug(db, slug)
        if not game:
            scan_errors_total.labels(reason="unknown_slug").inc()
            raise HTTPException(status_code=404, detail="Spil ikke fundet")

        scan = Scan(
            game_id=game.id,
            table_location=table_location,
            user_agent=request.headers.get("user-agent"),
            ip_hash=_hash_ip(_client_ip(request)),
        )
        db.add(scan)
        db.flush()
        rank = monthly_scan_rank(db, game.id)
        scans_total.labels(game=game.slug).inc()
        db.expunge(game)  # safe to use after session closes
        return game, rank


@app.get("/scan/{slug}")
@app.get("/scan/{slug}/{table_location}")
def scan_game(request: Request, slug: str, table_location: Optional[str] = None):
    try:
        game, rank = _record_scan(request, slug, table_location)
    except HTTPException:
        raise
    except Exception:
        scan_errors_total.labels(reason="db_error").inc()
        raise HTTPException(status_code=500, detail="Kunne ikke gemme scanning")

    with get_db() as db:
        top5 = top_games(db, days=7, limit=5)

    wiki_slug = game.name.replace(" ", "_")
    return templates.TemplateResponse(
        request,
        "thanks.html",
        {
            "game": game,
            "rank": rank,
            "top5": top5,
            "wiki_url": f"https://da.wikipedia.org/wiki/{wiki_slug}",
        },
    )


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


@app.get("/admin/qrcodes")
def admin_qrcodes(request: Request):
    """Generate PNG QR codes and render printable grid."""
    with get_db() as db:
        games = list(db.scalars(select(Game).order_by(Game.name)).all())
        for game in games:
            db.expunge(game)

    for game in games:
        url = f"{BASE_URL}/scan/{game.slug}"
        img = qrcode.make(url, box_size=8, border=2)
        out = QRCODE_DIR / f"{game.slug}.png"
        img.save(out)

    return templates.TemplateResponse(
        request,
        "qrcodes.html",
        {"games": games, "base_url": BASE_URL},
    )


@app.get("/qrcodes/{slug}.png")
def serve_qrcode(slug: str):
    path = QRCODE_DIR / f"{slug}.png"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="QR ikke genereret endnu")
    return FileResponse(path, media_type="image/png")
