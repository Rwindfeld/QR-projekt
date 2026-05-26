"""Pre-generate QR PNG files at deploy/build time (fast /admin/qrcodes page)."""
from __future__ import annotations

import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import qrcode

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from games_catalog import GAMES as GAMES_CORE  # noqa: E402

try:
    from games_catalog_bulk import GAMES_BULK  # noqa: E402
except ImportError:
    GAMES_BULK = []

BASE_URL = (
    os.getenv("RENDER_EXTERNAL_URL")
    or os.getenv("BASE_URL")
    or "https://qr-spilcafe.onrender.com"
).rstrip("/")
OUT_DIR = ROOT / "static" / "qrcodes"
WORKERS = min(8, (os.cpu_count() or 4))


def _write_one(slug: str) -> str:
    out = OUT_DIR / f"{slug}.png"
    if out.is_file():
        return slug
    url = f"{BASE_URL}/scan/{slug}"
    img = qrcode.make(url, box_size=6, border=2)
    img.save(out, optimize=True)
    return slug


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    slugs = [g["slug"] for g in GAMES_CORE + GAMES_BULK]
    if not slugs:
        print("No games in catalog")
        return

    created = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(_write_one, slug): slug for slug in slugs}
        for fut in as_completed(futures):
            fut.result()
            created += 1

    print(f"OK - {created} QR codes in {OUT_DIR} (base {BASE_URL})")


if __name__ == "__main__":
    main()
