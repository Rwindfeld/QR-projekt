"""Regenerate seed.sql and wiki_urls.py from scripts/games_catalog.py"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from games_catalog import GAMES as GAMES_CORE  # noqa: E402

try:
    from games_catalog_bulk import GAMES_BULK  # noqa: E402
except ImportError:
    GAMES_BULK = []

GAMES = GAMES_CORE + GAMES_BULK


def _sql_str(s: str) -> str:
    return s.replace("'", "''")


def _is_direct_wikipedia(url: str) -> bool:
    if not url:
        return False
    if "Special:" in url:
        return False
    return "/wiki/" in url


def main() -> None:
    lines = [
        "-- Auto-generated from scripts/games_catalog.py — do not edit by hand",
        "-- Run: python scripts/build_game_assets.py",
        "",
        "INSERT INTO games (slug, name, year_published, awards, fun_fact, wikipedia_url) VALUES",
    ]
    rows = []
    for g in GAMES:
        wiki = (g.get("wiki") or "").strip()
        wiki_sql = f"'{_sql_str(wiki)}'" if _is_direct_wikipedia(wiki) else "NULL"
        rows.append(
            f"(\n"
            f"    '{_sql_str(g['slug'])}',\n"
            f"    '{_sql_str(g['name'])}',\n"
            f"    {g['year']},\n"
            f"    '{_sql_str(g['awards'])}',\n"
            f"    '{_sql_str(g['fun_fact'])}',\n"
            f"    {wiki_sql}\n"
            f")"
        )
    lines.append(",\n".join(rows))
    lines.append(
        "ON CONFLICT (slug) DO UPDATE SET\n"
        "    name = EXCLUDED.name,\n"
        "    year_published = EXCLUDED.year_published,\n"
        "    awards = EXCLUDED.awards,\n"
        "    fun_fact = EXCLUDED.fun_fact,\n"
        "    wikipedia_url = EXCLUDED.wikipedia_url;\n"
    )
    (ROOT / "seed.sql").write_text("\n".join(lines), encoding="utf-8")

    wiki_lines = [
        '"""Verified Wikipedia article URLs (direct links only — no search fallbacks)."""',
        "",
        "from __future__ import annotations",
        "",
        "WIKIPEDIA_BY_SLUG: dict[str, str] = {",
    ]
    verified = 0
    for g in GAMES_CORE:
        wiki = (g.get("wiki") or "").strip()
        if _is_direct_wikipedia(wiki):
            wiki_lines.append(f'    "{g["slug"]}": "{wiki}",')
            verified += 1
    wiki_lines.extend(
        [
            "}",
            "",
            "",
            "def is_direct_wikipedia_article(url: str | None) -> bool:",
            '    """True only for direct /wiki/ article URLs (not Special:Search)."""',
            "    if not url:",
            "        return False",
            '    if "Special:" in url:',
            "        return False",
            '    return "/wiki/" in url',
            "",
            "",
            "def wikipedia_url_for_slug(slug: str) -> str | None:",
            "    url = WIKIPEDIA_BY_SLUG.get(slug)",
            "    return url if is_direct_wikipedia_article(url) else None",
            "",
            "",
            "def resolve_wikipedia_url(slug: str, db_url: str | None = None) -> str | None:",
            "    if is_direct_wikipedia_article(db_url):",
            "        return db_url",
            "    return wikipedia_url_for_slug(slug)",
            "",
        ]
    )
    (ROOT / "wiki_urls.py").write_text("\n".join(wiki_lines), encoding="utf-8")

    weights = {g["slug"]: g.get("weight", 2) for g in GAMES}
    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "game_weights.json").write_text(
        json.dumps(weights, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"OK — {len(GAMES)} games -> seed.sql; {verified} verified wiki URLs in wiki_urls.py")


if __name__ == "__main__":
    main()
