"""SQLAlchemy models and session helpers for QR café tracking."""

from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Generator, Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    create_engine,
    func,
    select,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

def _database_url() -> str:
    url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:1590@localhost:5432/QR",
    )
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if "render.com" in url and "sslmode=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"
    return url


DATABASE_URL = _database_url()

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    year_published: Mapped[Optional[int]] = mapped_column(SmallInteger)
    awards: Mapped[Optional[str]] = mapped_column(Text)
    fun_fact: Mapped[str] = mapped_column(Text, nullable=False)
    wikipedia_url: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    scans: Mapped[list["Scan"]] = relationship(back_populates="game")


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"))
    scanned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    table_location: Mapped[Optional[str]] = mapped_column(String(32))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    ip_hash: Mapped[Optional[str]] = mapped_column(String(64))

    game: Mapped["Game"] = relationship(back_populates="scans")


@contextmanager
def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_game_by_slug(db: Session, slug: str) -> Optional[Game]:
    return db.execute(select(Game).where(Game.slug == slug)).scalar_one_or_none()


def monthly_scan_rank(db: Session, game_id: int) -> int:
    """1-based rank: how many scans this calendar month for this game (including current)."""
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    count = db.execute(
        select(func.count())
        .select_from(Scan)
        .where(Scan.game_id == game_id, Scan.scanned_at >= month_start)
    ).scalar_one()
    return int(count)


def top_games(db: Session, days: int = 7, limit: int = 5) -> list[tuple[str, int]]:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = db.execute(
        select(Game.name, func.count(Scan.id).label("cnt"))
        .join(Scan, Scan.game_id == Game.id)
        .where(Scan.scanned_at >= since)
        .group_by(Game.id, Game.name)
        .order_by(func.count(Scan.id).desc())
        .limit(limit)
    ).all()
    return [(r[0], int(r[1])) for r in rows]
