"""Tests de l'historique : chaque utilisateur ne voit que ses propres simulations."""
import uuid

from fastapi.testclient import TestClient

from app.main import app

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


def new_user() -> dict:
    """Crée un compte avec un email unique et renvoie l'en-tête d'authentification."""
    email = f"test-{uuid.uuid4().hex[:8]}@exemple.fr"
    token = client.post("/auth/register",
                        json={"email": email, "password": "motdepasse123"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_history_requires_login():
    assert client.get("/history").status_code == 401
    assert client.post("/history", json=SAVE).status_code == 401


def test_save_list_and_delete():
    auth = new_user()
    saved = client.post("/history", json=SAVE, headers=auth)
    assert saved.status_code == 201
    body = saved.json()
    assert body["name"] == "Voiture raisonnable"
    assert 0 <= body["health_score"] <= 100

    assert [s["id"] for s in client.get("/history", headers=auth).json()] == [body["id"]]
    assert client.delete(f"/history/{body['id']}", headers=auth).status_code == 204
    assert client.get("/history", headers=auth).json() == []


def test_newest_first():
    auth = new_user()
    first = client.post("/history", json={**SAVE, "name": "Premier"}, headers=auth).json()
    second = client.post("/history", json={**SAVE, "name": "Second"}, headers=auth).json()
    ids = [s["id"] for s in client.get("/history", headers=auth).json()]
    assert ids == [second["id"], first["id"]]


def test_users_cannot_see_or_delete_each_other():
    alice, bob = new_user(), new_user()
    saved = client.post("/history", json=SAVE, headers=alice).json()
    assert client.get("/history", headers=bob).json() == []
    assert client.delete(f"/history/{saved['id']}", headers=bob).status_code == 404


def test_delete_unknown_returns_404():
    assert client.delete("/history/999999", headers=new_user()).status_code == 404


def test_empty_name_is_rejected():
    assert client.post("/history", json={**SAVE, "name": ""}, headers=new_user()).status_code == 422