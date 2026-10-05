"""Tests de l'historique, sur une base SQLite en mémoire (pas besoin de Docker)."""
from fastapi.testclient import TestClient
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
client = TestClient(app)

SAVE = {
    "name": "Voiture raisonnable",
    "profile": {"monthly_income": 2500, "monthly_expenses": 1700, "cash": 12000,
                "annual_inflation": 0.03},
    "decision": {"name": "Voiture", "price": 25000, "down_payment": 5000,
                 "loan_annual_rate": 0.065, "loan_months": 60,
                 "asset_annual_depreciation": 0.12, "extra_monthly_cost": 200},
    "horizon_months": 36,
}


def test_save_list_and_delete():
    saved = client.post("/history", json=SAVE)
    assert saved.status_code == 201
    body = saved.json()
    assert body["name"] == "Voiture raisonnable"
    assert 0 <= body["health_score"] <= 100

    listed = client.get("/history").json()
    assert any(s["id"] == body["id"] for s in listed)

    assert client.delete(f"/history/{body['id']}").status_code == 204
    assert all(s["id"] != body["id"] for s in client.get("/history").json())


def test_newest_first():
    first = client.post("/history", json={**SAVE, "name": "Premier"}).json()
    second = client.post("/history", json={**SAVE, "name": "Second"}).json()
    ids = [s["id"] for s in client.get("/history").json()]
    assert ids.index(second["id"]) < ids.index(first["id"])


def test_delete_unknown_returns_404():
    assert client.delete("/history/999999").status_code == 404


def test_empty_name_is_rejected():
    assert client.post("/history", json={**SAVE, "name": ""}).status_code == 422