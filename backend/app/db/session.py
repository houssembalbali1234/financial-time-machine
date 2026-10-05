"""Connexion à la base de données."""
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    """Classe mère de toutes les tables."""


def get_db() -> Iterator[Session]:
    """Ouvre une session pour une requête, puis la ferme."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()