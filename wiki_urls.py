"""Verified Wikipedia article URLs (direct links only — no search fallbacks)."""

from __future__ import annotations

WIKIPEDIA_BY_SLUG: dict[str, str] = {
    "ticket-to-ride": "https://da.wikipedia.org/wiki/Ticket_to_Ride_(spil)",
    "catan": "https://da.wikipedia.org/wiki/Settlers",
    "carcassonne": "https://en.wikipedia.org/wiki/Carcassonne_(board_game)",
    "azul": "https://en.wikipedia.org/wiki/Azul_(board_game)",
    "wingspan": "https://en.wikipedia.org/wiki/Wingspan_(board_game)",
    "7-wonders": "https://en.wikipedia.org/wiki/7_Wonders_(board_game)",
    "splendor": "https://en.wikipedia.org/wiki/Splendor_(board_game)",
    "codenames": "https://en.wikipedia.org/wiki/Codenames_(board_game)",
    "pandemic": "https://en.wikipedia.org/wiki/Pandemic_(board_game)",
    "dixit": "https://en.wikipedia.org/wiki/Dixit_(board_game)",
    "king-of-tokyo": "https://en.wikipedia.org/wiki/King_of_Tokyo",
    "terraforming-mars": "https://en.wikipedia.org/wiki/Terraforming_Mars_(board_game)",
    "kingdomino": "https://en.wikipedia.org/wiki/Kingdomino",
    "sushi-go": "https://en.wikipedia.org/wiki/Sushi_Go!",
    "patchwork": "https://en.wikipedia.org/wiki/Patchwork_(board_game)",
    "root": "https://en.wikipedia.org/wiki/Root_(board_game)",
    "everdell": "https://en.wikipedia.org/wiki/Everdell",
    "cascadia": "https://en.wikipedia.org/wiki/Cascadia_(board_game)",
    "exploding-kittens": "https://en.wikipedia.org/wiki/Exploding_Kittens",
    "the-quacks-of-quedlinburg": "https://en.wikipedia.org/wiki/The_Quacks_of_Quedlinburg",
    "love-letter": "https://en.wikipedia.org/wiki/Love_Letter_(card_game)",
    "scythe": "https://en.wikipedia.org/wiki/Scythe_(board_game)",
    "klask": "https://da.wikipedia.org/wiki/Klask",
    "risk": "https://da.wikipedia.org/wiki/Risk",
    "monopoly": "https://da.wikipedia.org/wiki/Matador_(br%C3%A6tspil)",
    "spirit-island": "https://en.wikipedia.org/wiki/Spirit_Island_(board_game)",
    "hanabi": "https://en.wikipedia.org/wiki/Hanabi_(card_game)",
    "fluxx": "https://en.wikipedia.org/wiki/Fluxx",
    "uno": "https://da.wikipedia.org/wiki/Uno_(kortspil)",
    "jungle-speed": "https://en.wikipedia.org/wiki/Jungle_Speed",
    "one-night-ultimate-werewolf": "https://en.wikipedia.org/wiki/One_Night_Ultimate_Werewolf",
    "the-resistance": "https://en.wikipedia.org/wiki/The_Resistance_(party_game)",
    "secret-hitler": "https://en.wikipedia.org/wiki/Secret_Hitler",
    "coup": "https://en.wikipedia.org/wiki/Coup_(card_game)",
    "skull": "https://en.wikipedia.org/wiki/Skull_(board_game)",
    "betrayal-at-house-on-the-hill": "https://en.wikipedia.org/wiki/Betrayal_at_House_on_the_Hill",
    "small-world": "https://en.wikipedia.org/wiki/Small_World_(board_game)",
    "dominion": "https://en.wikipedia.org/wiki/Dominion_(card_game)",
    "7-wonders-duel": "https://en.wikipedia.org/wiki/7_Wonders_Duel",
    "jaipur": "https://en.wikipedia.org/wiki/Jaipur_(board_game)",
    "lost-cities": "https://en.wikipedia.org/wiki/Lost_Cities",
    "hive": "https://en.wikipedia.org/wiki/Hive_(game)",
    "onitama": "https://en.wikipedia.org/wiki/Onitama",
    "santorini": "https://en.wikipedia.org/wiki/Santorini_(board_game)",
    "telestrations": "https://en.wikipedia.org/wiki/Telestrations",
    "just-one": "https://en.wikipedia.org/wiki/Just_One_(board_game)",
    "decrypto": "https://en.wikipedia.org/wiki/Decrypto",
    "the-mind": "https://en.wikipedia.org/wiki/The_Mind_(card_game)",
    "no-thanks": "https://en.wikipedia.org/wiki/No_Thanks!_(card_game)",
    "diamant": "https://en.wikipedia.org/wiki/Incan_Gold",
    "camel-up": "https://en.wikipedia.org/wiki/Camel_Up",
    "colt-express": "https://en.wikipedia.org/wiki/Colt_Express",
    "qwirkle": "https://en.wikipedia.org/wiki/Qwirkle",
    "blokus": "https://en.wikipedia.org/wiki/Blokus",
    "parks": "https://en.wikipedia.org/wiki/Parks_(board_game)",
    "ark-nova": "https://en.wikipedia.org/wiki/Ark_Nova",
    "stone-age": "https://en.wikipedia.org/wiki/Stone_Age_(board_game)",
    "lords-of-waterdeep": "https://en.wikipedia.org/wiki/Lords_of_Waterdeep",
    "castles-of-burgundy": "https://en.wikipedia.org/wiki/The_Castles_of_Burgundy",
    "heat-pedal-to-the-metal": "https://en.wikipedia.org/wiki/Heat:_Pedal_to_the_Metal",
    "brass-birmingham": "https://en.wikipedia.org/wiki/Brass:_Birmingham",
    "blood-rage": "https://en.wikipedia.org/wiki/Blood_Rage_(board_game)",
    "power-grid": "https://en.wikipedia.org/wiki/Power_Grid",
    "race-for-the-galaxy": "https://en.wikipedia.org/wiki/Race_for_the_Galaxy",
    "the-crew": "https://en.wikipedia.org/wiki/The_Crew_(card_game)",
    "rhino-hero": "https://en.wikipedia.org/wiki/Rhino_Hero",
    "timeline": "https://en.wikipedia.org/wiki/Timeline_(card_game)",
    "hitster": "https://en.wikipedia.org/wiki/Hitster",
    "so-clover": "https://en.wikipedia.org/wiki/So_Clover!",
    "scout": "https://en.wikipedia.org/wiki/Scout_(card_game)",
    "forbidden-island": "https://en.wikipedia.org/wiki/Forbidden_Island",
    "forbidden-desert": "https://en.wikipedia.org/wiki/Forbidden_Desert",
    "flash-point-fire-rescue": "https://en.wikipedia.org/wiki/Flash_Point:_Fire_Rescue",
    "mysterium": "https://en.wikipedia.org/wiki/Mysterium_(board_game)",
    "dead-of-winter": "https://en.wikipedia.org/wiki/Dead_of_Winter:_A_Crossroads_Game",
    "bang-the-dice-game": "https://en.wikipedia.org/wiki/Bang!_(card_game)",
    "clank": "https://en.wikipedia.org/wiki/Clank!_A_Deck-Building_Adventure",
    "quest-for-el-dorado": "https://en.wikipedia.org/wiki/The_Quest_for_El_Dorado",
    "gloomhaven-jaws-of-the-lion": "https://en.wikipedia.org/wiki/Gloomhaven",
    "monopoly-deal": "https://en.wikipedia.org/wiki/Monopoly_Deal",
    "scrabble": "https://da.wikipedia.org/wiki/Scrabble",
    "cluedo": "https://da.wikipedia.org/wiki/Cluedo",
    "backgammon": "https://da.wikipedia.org/wiki/Backgammon",
    "sequence": "https://en.wikipedia.org/wiki/Sequence_(game)",
    "abalone": "https://en.wikipedia.org/wiki/Abalone_(board_game)",
    "pentago": "https://en.wikipedia.org/wiki/Pentago",
    "werewolf": "https://en.wikipedia.org/wiki/Mafia_(party_game)",
    "taboo": "https://en.wikipedia.org/wiki/Taboo_(game)",
    "sushi-go-party": "https://en.wikipedia.org/wiki/Sushi_Go!",
    "werewords": "https://en.wikipedia.org/wiki/Werewords",
    "wavelength": "https://en.wikipedia.org/wiki/Wavelength_(game)",
    "cartographers": "https://en.wikipedia.org/wiki/Cartographers_(board_game)",
    "viticulture": "https://en.wikipedia.org/wiki/Viticulture_(board_game)",
    "tapestry": "https://en.wikipedia.org/wiki/Tapestry_(board_game)",
    "star-realms": "https://en.wikipedia.org/wiki/Star_Realms",
    "marvel-champions": "https://en.wikipedia.org/wiki/Marvel_Champions:_The_Card_Game",
    "calico": "https://en.wikipedia.org/wiki/Calico_(board_game)",
    "planet": "https://en.wikipedia.org/wiki/Planet_(board_game)",
    "my-little-scythe": "https://en.wikipedia.org/wiki/My_Little_Scythe",
}


def is_direct_wikipedia_article(url: str | None) -> bool:
    """True only for direct /wiki/ article URLs (not Special:Search)."""
    if not url:
        return False
    if "Special:" in url:
        return False
    return "/wiki/" in url


def wikipedia_url_for_slug(slug: str) -> str | None:
    url = WIKIPEDIA_BY_SLUG.get(slug)
    return url if is_direct_wikipedia_article(url) else None


def resolve_wikipedia_url(slug: str, db_url: str | None = None) -> str | None:
    if is_direct_wikipedia_article(db_url):
        return db_url
    return wikipedia_url_for_slug(slug)
