from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

PAYLOAD = {
    "profile": {
        "monthly_income": 2800,
        "monthly_expenses": 1700,
        "cash": 15000,
        "annual_inflation": 0.06,
    },
    "decision": {
        "name": "Voiture",
        "price": 45000,
        "down_payment": 10000,
        "loan_annual_rate": 0.095,
        "loan_months": 60,
        "asset_annual_depreciation": 0.12,
        "extra_monthly_cost": 150,
    },
    "horizon_months": 36,
}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_simulation_returns_all_months():
    response = client.post("/simulations", json=PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert len(body["months"]) == 36
    assert body["summary"]["final_cash"] == 7225.004
    assert body["summary"]["final_debt"] > 0


def test_simulation_without_decision():
    response = client.post("/simulations",
                           json={"profile": PAYLOAD["profile"], "horizon_months": 12})
    assert response.status_code == 200
    assert response.json()["summary"]["final_debt"] == 0


def test_down_payment_above_price_is_rejected():
    bad = {**PAYLOAD, "decision": {**PAYLOAD["decision"], "down_payment": 50000}}
    assert client.post("/simulations", json=bad).status_code == 422


def test_invalid_horizon_is_rejected():
    bad = {**PAYLOAD, "horizon_months": 18}
    assert client.post("/simulations", json=bad).status_code == 422


def test_rate_in_percent_is_rejected():
    # 9.5 au lieu de 0.095 : erreur classique qu'on veut bloquer
    bad = {**PAYLOAD, "decision": {**PAYLOAD["decision"], "loan_annual_rate": 9.5}}
    assert client.post("/simulations", json=bad).status_code == 422