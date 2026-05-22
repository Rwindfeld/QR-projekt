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
}


def wikipedia_url_for_slug(slug: str) -> str:
    return WIKIPEDIA_BY_SLUG.get(
        slug,
        f"https://da.wikipedia.org/wiki/Special:Search?search={slug.replace('-', '+')}",
    )
