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





# ---------- Comparaison de scénarios ----------

def scenarios_for(cash: float) -> dict:
    payload = {**PAYLOAD, "profile": {**PAYLOAD["profile"], "cash": cash}}
    response = client.post("/simulations/scenarios", json=payload)
    assert response.status_code == 200
    return response.json()


def test_scenarios_returns_four_variants():
    body = scenarios_for(15000)
    keys = {s["key"] for s in body["scenarios"]}
    assert keys == {"maintenant", "dans_6_mois", "dans_12_mois", "moins_cher"}


def test_rich_profile_can_buy_now():
    assert scenarios_for(30000)["recommended"] == "maintenant"


def test_tight_profile_is_told_to_wait():
    # Avec 15 000 TND, acheter maintenant laisse moins de 3 mois de sorties
    assert scenarios_for(15000)["recommended"] == "dans_6_mois"


def test_recommended_scenario_keeps_safety_cushion():
    # La recommandation ne doit jamais contredire la règle de sécurité
    body = scenarios_for(15000)
    best = next(s for s in body["scenarios"] if s["key"] == body["recommended"])
    summary = best["summary"]
    assert summary["min_cash"] >= 3 * summary["max_monthly_outflow"]


def test_scenarios_require_a_decision():
    payload = {"profile": PAYLOAD["profile"], "horizon_months": 36}
    assert client.post("/simulations/scenarios", json=payload).status_code == 422


# ---------- Stress test ----------

STRESS = {
    **PAYLOAD,
    "shock": {"name": "perte_emploi", "income_factor": 0, "start_month": 6,
              "duration_months": 3},
}


def test_stress_test_loses_three_salaries():
    response = client.post("/simulations/stress-test", json=STRESS)
    assert response.status_code == 200
    body = response.json()
    assert body["cash_lost"] == 8400.0
    assert body["stressed"]["final_cash"] < body["baseline"]["final_cash"]
    assert body["stressed"]["max_debt_ratio"] == 1.0


def test_invalid_shock_is_rejected():
    bad = {**STRESS, "shock": {**STRESS["shock"], "income_factor": 1.5}}
    assert client.post("/simulations/stress-test", json=bad).status_code == 422