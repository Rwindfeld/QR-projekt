"""Drikkevarerabat: 5 % pr. nyt spil, med anti-misbrug."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional
try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None  # type: ignore[misc, assignment]

from fastapi import Request, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models import Scan

VISITOR_COOKIE = "qr_visitor"
VISITOR_COOKIE_MAX_AGE = 86_400  # 24 timer

DISCOUNT_PCT_PER_GAME = 5
DISCOUNT_MAX_TOTAL_PCT = 50
SAME_GAME_COOLDOWN = timedelta(minutes=2)
MAX_DISCOUNT_GAMES_PER_DAY = 15

def _copenhagen_tz():
    if ZoneInfo is not None:
        return ZoneInfo("Europe/Copenhagen")
    return timezone(timedelta(hours=1))


TZ = _copenhagen_tz()


@dataclass(frozen=True)
class DiscountResult:
    earned_pct: int
    total_pct: int
    eligible: bool
    reason: Optional[str]  # kort dansk forklaring når ikke eligible
    games_with_discount_today: int
    visitor_token: str
    bar_code: str


def _day_start_utc(now: datetime) -> datetime:
    local = now.astimezone(TZ)
    start_local = local.replace(hour=0, minute=0, second=0, microsecond=0)
    return start_local.astimezone(timezone.utc)


def _bar_code(visitor_token: str, day: datetime) -> str:
    """Kort kode til visning i baren (ikke hemmelighed, kun identifikation)."""
    day_key = day.astimezone(TZ).strftime("%Y%m%d")
    digest = hashlib.sha256(f"{visitor_token}:{day_key}".encode()).hexdigest()
    return digest[:6].upper()


def visitor_token_from_request(request: Request) -> tuple[str, bool]:
    """Returner (token, skal_cookie_sættes)."""
    raw = request.cookies.get(VISITOR_COOKIE)
    if raw and len(raw) >= 32:
        try:
            uuid.UUID(raw)
            return raw, False
        except ValueError:
            pass
    return str(uuid.uuid4()), True


def set_visitor_cookie(response: Response, token: str) -> None:
    import os

    base = (
        os.getenv("BASE_URL")
        or os.getenv("RENDER_EXTERNAL_URL")
        or "http://localhost:8000"
    )
    response.set_cookie(
        key=VISITOR_COOKIE,
        value=token,
        max_age=VISITOR_COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=base.lower().startswith("https"),
    )


def _total_discount_pct_today(db: Session, visitor_token: str, day_start: datetime) -> int:
    total = db.execute(
        select(func.coalesce(func.sum(Scan.discount_pct), 0))
        .where(
            Scan.visitor_token == visitor_token,
            Scan.discount_eligible.is_(True),
            Scan.scanned_at >= day_start,
        )
    ).scalar_one()
    return int(total)


def _games_with_discount_today(db: Session, visitor_token: str, day_start: datetime) -> int:
    count = db.execute(
        select(func.count())
        .select_from(Scan)
        .where(
            Scan.visitor_token == visitor_token,
            Scan.discount_eligible.is_(True),
            Scan.scanned_at >= day_start,
        )
    ).scalar_one()
    return int(count)


def evaluate_discount(
    db: Session,
    visitor_token: str,
    game_id: int,
    now: Optional[datetime] = None,
) -> DiscountResult:
    """
    Afgør om denne scanning giver +5 % drikkevarerabat.

    Regler:
    - Samme spil scannet inden for 2 min → ingen rabat (anti-spam).
    - Samme spil har allerede givet rabat i dag → ingen ekstra rabat.
    - Max 15 spil med rabat pr. besøg/dag.
    - Max 50 % samlet rabat på drikkevarer.
    """
    now = now or datetime.now(timezone.utc)
    day_start = _day_start_utc(now)
    total_before = _total_discount_pct_today(db, visitor_token, day_start)
    games_before = _games_with_discount_today(db, visitor_token, day_start)
    bar = _bar_code(visitor_token, now)

    cooldown_since = now - SAME_GAME_COOLDOWN
    recent_same = db.execute(
        select(Scan.id)
        .where(
            Scan.visitor_token == visitor_token,
            Scan.game_id == game_id,
            Scan.scanned_at >= cooldown_since,
        )
        .limit(1)
    ).first()
    if recent_same:
        return DiscountResult(
            earned_pct=0,
            total_pct=total_before,
            eligible=False,
            reason="Du har lige scannet dette spil — vent mindst 2 minutter før du scanner det igen.",
            games_with_discount_today=games_before,
            visitor_token=visitor_token,
            bar_code=bar,
        )

    already_game = db.execute(
        select(Scan.id)
        .where(
            Scan.visitor_token == visitor_token,
            Scan.game_id == game_id,
            Scan.discount_eligible.is_(True),
            Scan.scanned_at >= day_start,
        )
        .limit(1)
    ).first()
    if already_game:
        return DiscountResult(
            earned_pct=0,
            total_pct=total_before,
            eligible=False,
            reason="Du har allerede fået rabat for dette spil i dag. Prøv et andet spil fra hylden.",
            games_with_discount_today=games_before,
            visitor_token=visitor_token,
            bar_code=bar,
        )

    if games_before >= MAX_DISCOUNT_GAMES_PER_DAY:
        return DiscountResult(
            earned_pct=0,
            total_pct=total_before,
            eligible=False,
            reason=f"Du har nået grænsen på {MAX_DISCOUNT_GAMES_PER_DAY} spil med rabat i dag.",
            games_with_discount_today=games_before,
            visitor_token=visitor_token,
            bar_code=bar,
        )

    if total_before >= DISCOUNT_MAX_TOTAL_PCT:
        return DiscountResult(
            earned_pct=0,
            total_pct=total_before,
            eligible=False,
            reason=f"Maksimal drikkevarerabat ({DISCOUNT_MAX_TOTAL_PCT} %) er allerede opnået i dag.",
            games_with_discount_today=games_before,
            visitor_token=visitor_token,
            bar_code=bar,
        )

    earned = min(
        DISCOUNT_PCT_PER_GAME,
        DISCOUNT_MAX_TOTAL_PCT - total_before,
    )
    if earned <= 0:
        return DiscountResult(
            earned_pct=0,
            total_pct=total_before,
            eligible=False,
            reason=f"Maksimal drikkevarerabat ({DISCOUNT_MAX_TOTAL_PCT} %) er allerede opnået i dag.",
            games_with_discount_today=games_before,
            visitor_token=visitor_token,
            bar_code=bar,
        )

    return DiscountResult(
        earned_pct=earned,
        total_pct=total_before + earned,
        eligible=True,
        reason=None,
        games_with_discount_today=games_before + 1,
        visitor_token=visitor_token,
        bar_code=bar,
    )
