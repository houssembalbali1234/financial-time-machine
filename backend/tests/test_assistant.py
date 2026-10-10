"""Tests de l'assistant financier, sans appeler la vraie IA."""
from fastapi.testclient import TestClient

from app.ai.assistant import build_context, build_messages, invented_numbers
from app.api.routes.ai import get_chat_model
from app.engine import Decision, FinancialProfile
from app.main import app

client = TestClient(app)

PROFILE = FinancialProfile(monthly_income=2500, monthly_expenses=1700, cash=12000,
                           annual_inflation=0.03)
CAR = Decision(name="Voiture", price=30000, down_payment=6000, loan_annual_rate=0.065,
               loan_months=60, asset_annual_depreciation=0.12, extra_monthly_cost=200)
CONTEXT, ALLOWED = build_context(PROFILE, CAR, 36)

PAYLOAD = {
    "profile": {"monthly_income": 2500, "monthly_expenses": 1700, "cash": 12000,
                "annual_inflation": 0.03},
    "decision": {"name": "Voiture", "price": 30000, "down_payment": 6000,
                 "loan_annual_rate": 0.065, "loan_months": 60,
                 "asset_annual_depreciation": 0.12, "extra_monthly_cost": 200},
    "horizon_months": 36,
    "question": "Et si j'attendais un an ?",
}


def use_chat(model):
    app.dependency_overrides[get_chat_model] = lambda: model


def teardown_function():
    app.dependency_overrides.pop(get_chat_model, None)


def test_context_contains_the_engine_results():
    for text in ["30 000 €", "8 000 €", "38 100 €", "470 €", "51/100", "attendre 12 mois",
                 "16 000 €", "perte d'emploi"]:
        assert text in CONTEXT


def test_messages_keep_only_recent_history():
    history = [{"role": "user", "content": f"q{i}"} for i in range(10)]
    messages = build_messages(CONTEXT, "nouvelle question", history)
    assert messages[0]["role"] == "system" and CONTEXT in messages[0]["content"]
    assert len(messages) == 1 + 6 + 1
    assert messages[-1] == {"role": "user", "content": "nouvelle question"}


def test_invented_amounts_are_detected():
    assert invented_numbers("Votre épargne serait de 8 000 € dans 3 ans.", ALLOWED) == []
    assert invented_numbers("Vous auriez 55 000 € de côté.", ALLOWED) == [55000]


def test_answer_with_known_numbers_is_verified():
    use_chat(lambda messages: "En attendant 12 mois, votre épargne serait de 16 000 € dans 3 ans.")
    body = client.post("/ai/ask", json=PAYLOAD).json()
    assert body["verified"] is True


def test_invented_amount_triggers_one_retry():
    calls = []

    def model(messages):
        calls.append(messages)
        return "Vous auriez 55 000 €." if len(calls) == 1 else "Votre épargne serait de 8 000 €."

    use_chat(model)
    body = client.post("/ai/ask", json=PAYLOAD).json()
    assert len(calls) == 2
    assert "55000" in calls[1][-1]["content"]
    assert body == {"answer": "Votre épargne serait de 8 000 €.", "verified": True}


def test_history_is_sent_to_the_model():
    seen = []
    use_chat(lambda messages: seen.append(messages) or "D'accord.")
    payload = {**PAYLOAD, "history": [{"role": "user", "content": "Bonjour"},
                                      {"role": "assistant", "content": "Bonjour !"}]}
    client.post("/ai/ask", json=payload)
    assert [m["content"] for m in seen[0][1:3]] == ["Bonjour", "Bonjour !"]


def test_empty_question_is_rejected():
    assert client.post("/ai/ask", json={**PAYLOAD, "question": ""}).status_code == 422


def test_llama_errors_become_502():
    def broken(messages):
        raise RuntimeError("réseau coupé")

    use_chat(broken)
    assert client.post("/ai/ask", json=PAYLOAD).status_code == 502