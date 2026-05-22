"""Verified Wikipedia URLs per game slug (da.wikipedia when available, else en)."""

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
}


def wikipedia_url_for_slug(slug: str) -> str:
    return WIKIPEDIA_BY_SLUG.get(
        slug,
        f"https://da.wikipedia.org/wiki/Special:Search?search={slug.replace('-', '+')}",
    )
