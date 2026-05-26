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


def main() -> None:
    lines = [
        "-- Auto-generated from scripts/games_catalog.py — do not edit by hand",
        "-- Run: python scripts/build_game_assets.py",
        "",
        "INSERT INTO games (slug, name, year_published, awards, fun_fact, wikipedia_url) VALUES",
    ]
    rows = []
    for g in GAMES:
        rows.append(
            f"(\n"
            f"    '{_sql_str(g['slug'])}',\n"
            f"    '{_sql_str(g['name'])}',\n"
            f"    {g['year']},\n"
            f"    '{_sql_str(g['awards'])}',\n"
            f"    '{_sql_str(g['fun_fact'])}',\n"
            f"    '{_sql_str(g['wiki'])}'\n"
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
        '"""Verified Wikipedia URLs per game slug (auto-generated)."""',
        "",
        "WIKIPEDIA_BY_SLUG: dict[str, str] = {",
    ]
    for g in GAMES:
        wiki_lines.append(f'    "{g["slug"]}": "{g["wiki"]}",')
    wiki_lines.extend(
        [
            "}",
            "",
            "",
            "def wikipedia_url_for_slug(slug: str) -> str:",
            "    return WIKIPEDIA_BY_SLUG.get(",
            "        slug,",
            '        f"https://da.wikipedia.org/wiki/Special:Search?search={slug.replace(\'-\', \'+\')}",',
            "    )",
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

    print(f"OK — {len(GAMES)} games -> seed.sql, wiki_urls.py, data/game_weights.json")


if __name__ == "__main__":
    main()
