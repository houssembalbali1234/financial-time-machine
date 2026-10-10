"""Tests de la Lettre du futur, sans appeler la vraie IA."""
import json

import httpx
from fastapi.testclient import TestClient

from app.ai.letter import build_facts, build_prompt
from app.ai.llm import make_ollama_writer
from app.api.routes.ai import get_letter_writer
from app.engine import Decision, FinancialProfile
from app.main import app

client = TestClient(app)

PROFILE = FinancialProfile(monthly_income=2500, monthly_expenses=1700, cash=12000,
                           annual_inflation=0.03)
CAR = Decision(name="Voiture", price=30000, down_payment=6000, loan_annual_rate=0.065,
               loan_months=60, asset_annual_depreciation=0.12, extra_monthly_cost=200)

PAYLOAD = {
    "profile": {"monthly_income": 2500, "monthly_expenses": 1700, "cash": 12000,
                "annual_inflation": 0.03},
    "decision": {"name": "Voiture", "price": 30000, "down_payment": 6000,
                 "loan_annual_rate": 0.065, "loan_months": 60,
                 "asset_annual_depreciation": 0.12, "extra_monthly_cost": 200},
    "horizon_months": 36,
}


def test_facts_come_from_the_engine():
    facts = build_facts(PROFILE, CAR, 36)
    assert facts.years == 3
    assert facts.final_cash_with == 7978
    assert facts.turning_month == 32
    assert facts.health_before == 100
    assert facts.health_after == 51


def test_prompt_contains_every_number():
    facts = build_facts(PROFILE, CAR, 36)
    prompt = build_prompt(facts)
    for number in ["30000", "7978", "mois 32", "100 aujourd'hui", "51 après"]:
        assert number in prompt


def test_letter_route_uses_the_writer():
    seen = {}

    def fake_writer(system: str, prompt: str) -> str:
        seen["prompt"] = prompt
        return "Cher moi d'aujourd'hui..."

    app.dependency_overrides[get_letter_writer] = lambda: fake_writer
    try:
        response = client.post("/ai/future-letter", json=PAYLOAD)
    finally:
        del app.dependency_overrides[get_letter_writer]

    assert response.status_code == 200
    assert response.json()["letter"] == "Cher moi d'aujourd'hui..."
    assert response.json()["facts"]["health_after"] == 51
    assert "7978" in seen["prompt"]


def test_ai_errors_become_502():
    def broken_writer(system: str, prompt: str) -> str:
        raise RuntimeError("réseau coupé")

    app.dependency_overrides[get_letter_writer] = lambda: broken_writer
    try:
        assert client.post("/ai/future-letter", json=PAYLOAD).status_code == 502
    finally:
        del app.dependency_overrides[get_letter_writer]


def test_ollama_request_and_answer_format():
    """Vérifie le dialogue avec Ollama grâce à un faux serveur (pas besoin d'Ollama installé)."""
    sent = {}

    def fake_ollama(request: httpx.Request) -> httpx.Response:
        sent["url"] = str(request.url)
        sent["body"] = json.loads(request.content)
        return httpx.Response(200, json={"message": {"role": "assistant", "content": "  Bonjour  "}})

    writer = make_ollama_writer("http://ollama:11434", "llama3.1:8b", 10,
                                client=httpx.Client(transport=httpx.MockTransport(fake_ollama)))
    assert writer("consigne", "situation") == "Bonjour"
    assert sent["url"] == "http://ollama:11434/api/chat"
    assert sent["body"]["model"] == "llama3.1:8b"
    assert sent["body"]["stream"] is False
    assert [m["role"] for m in sent["body"]["messages"]] == ["system", "user"]