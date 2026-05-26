"""Generate games_catalog_bulk.py with 500 extra café-catalog games."""
from __future__ import annotations

import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COUNT = 500
SEED = 42

ADJECTIVES = [
    "Arctic", "Baltic", "Cosmic", "Crystal", "Dragon", "Emerald", "Frozen",
    "Golden", "Hidden", "Iron", "Jade", "Kingdom", "Lunar", "Mystic", "Nordic",
    "Ocean", "Phantom", "Royal", "Shadow", "Silver", "Storm", "Sunset", "Timber",
    "Urban", "Viking", "Wild", "Ancient", "Brave", "Crimson", "Distant", "Eternal",
    "Forgotten", "Grand", "Harbor", "Ivory", "Jungle", "Knightly", "Lost", "Marble",
    "Neon", "Obsidian", "Primal", "Quiet", "Rustic", "Stellar", "Tidal", "Umber",
    "Velvet", "Whisper", "Zenith",
]
NOUNS = [
    "Alliance", "Arena", "Caravan", "Castle", "Citadel", "Colony", "Convoy",
    "Crown", "Dynasty", "Empire", "Expedition", "Fleet", "Forge", "Fortress",
    "Guild", "Harbor", "Horizon", "Isles", "Kingdom", "Legacy", "Market",
    "Outpost", "Quest", "Realm", "Republic", "Ridge", "Sanctuary", "Siege",
    "Spire", "Stronghold", "Temple", "Territory", "Towers", "Trade", "Tribe",
    "Valley", "Voyage", "Wastes", "Wilds", "Workshop", "Archive", "Bazaar",
    "Circuit", "Delta", "Echo", "Frontier", "Garden", "Haven", "Junction",
    "Labyrinth", "Monument", "Nexus", "Odyssey", "Parade", "Quarry", "Rail",
    "Summit", "Tavern", "Union", "Village", "Wonders", "Yard", "Zone",
]
SUFFIXES = ["", " II", " Deluxe", " Express", " Junior", " Legends", " Remix"]
AWARD_POOL = [
    "Café-katalog",
    "Populært hos gæster",
    "Niche-titel",
    "Klassiker på hylden",
    "Nyhed i sortimentet",
    "Familievenligt",
    "Strategi for entusiaster",
    "Hurtigt party-spil",
]
FUN_FACT_TEMPLATES = [
    "{name} er ofte det spil gæster tager ned, når de vil prøve noget nyt på hylden.",
    "Mange café-besøgende opdager {name} først via QR-koden — ikke via anbefaling ved disken.",
    "{name} passer godt til en aften, hvor gruppen vil have regler på under 20 minutter.",
    "Hylden med {name} bliver ofte tømt om lørdagen, når der kommer nye gæster ind.",
    "Ejer-notat: {name} er et godt mellemvalg mellem party og strategi.",
    "Gæster scanner ofte {name} for at læse regler, før de tager kassen med hjem til bordet.",
    "{name} ligger typisk i den midterste hylde — nem at overse, men stærk når den først findes.",
]


def slugify(text: str) -> str:
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def main() -> None:
    random.seed(SEED)
    sys_path = ROOT
    import sys

    sys.path.insert(0, str(sys_path))
    from games_catalog import GAMES  # noqa: E402

    used_slugs = {g["slug"] for g in GAMES}
    games: list[dict] = []

    for i in range(COUNT):
        for _ in range(200):
            adj = random.choice(ADJECTIVES)
            noun = random.choice(NOUNS)
            suffix = random.choice(SUFFIXES)
            name = f"{adj} {noun}{suffix}".strip()
            slug = f"{slugify(name)}-c{i + 1:03d}"
            if slug not in used_slugs:
                used_slugs.add(slug)
                break
        else:
            slug = f"cafe-game-c{i + 1:03d}"
            name = f"Café Game {i + 1}"

        year = random.randint(1975, 2024)
        awards = random.choice(AWARD_POOL)
        fun_fact = random.choice(FUN_FACT_TEMPLATES).format(name=name)
        # Ingen Wikipedia for auto-genererede katalogtitler (findes ikke som artikel)
        wiki = ""
        # Most bulk titles are rarely scanned; a few slightly more visible
        weight = random.choices([1, 1, 1, 1, 2, 2, 3], weights=[50, 20, 10, 5, 8, 5, 2])[0]

        games.append(
            {
                "slug": slug,
                "name": name,
                "year": year,
                "awards": awards,
                "fun_fact": fun_fact,
                "wiki": wiki,
                "weight": weight,
            }
        )

    lines = [
        '"""500 ekstra spil til café-kataloget (auto-genereret)."""',
        "",
        "GAMES_BULK = [",
    ]
    for g in games:
        lines.append("    {")
        lines.append(f'        "slug": "{g["slug"]}",')
        lines.append(f'        "name": "{g["name"]}",')
        lines.append(f'        "year": {g["year"]},')
        lines.append(f'        "awards": "{g["awards"]}",')
        lines.append(f'        "fun_fact": "{g["fun_fact"].replace(chr(39), chr(39)+chr(39))}",')
        lines.append(f'        "wiki": "{g["wiki"]}",')
        lines.append(f'        "weight": {g["weight"]},')
        lines.append("    },")
    lines.append("]")
    lines.append("")

    out = ROOT / "games_catalog_bulk.py"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"OK — wrote {len(games)} games to {out.name}")


if __name__ == "__main__":
    main()
