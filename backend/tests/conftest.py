"""Base de données de test partagée : SQLite en mémoire, pas besoin de Docker."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app

test_engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                            poolclass=StaticPool)
TestSession = sessionmaker(bind=test_engine)
Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db