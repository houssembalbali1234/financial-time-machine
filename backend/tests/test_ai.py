"""Tests de la Lettre du futur, sans appeler la vraie IA."""
import json

import httpx
from fastapi.testclient import TestClient

from app.ai.letter import assess, build_facts, build_prompt, check_letter, numbers_in
from app.ai.llm import make_ollama_writer
from app.api.routes.ai import get_letter_writer
from app.engine import Decision, FinancialProfile
from app.main import app

client = TestClient(app)

PROFILE = FinancialProfile(monthly_income=2500, monthly_expenses=1700, cash=12000,
                           annual_inflation=0.03)
CAR = Decision(name="Voiture", price=30000, down_payment=6000, loan_annual_rate=0.065,
               loan_months=60, asset_annual_depreciation=0.12, extra_monthly_cost=200)
FACTS = build_facts(PROFILE, CAR, 36)

PAYLOAD = {
    "profile": {"monthly_income": 2500, "monthly_expenses": 1700, "cash": 12000,
                "annual_inflation": 0.03},
    "decision": {"name": "Voiture", "price": 30000, "down_payment": 6000,
                 "loan_annual_rate": 0.065, "loan_months": 60,
                 "asset_annual_depreciation": 0.12, "extra_monthly_cost": 200},
    "horizon_months": 36,
}

GOOD_LETTER = """Cher toi,
Trois ans ont passé. J'ai ma voiture et environ 8 000 € d'épargne. Il me reste 10 500 € de crédit.
Sans la voiture, j'aurais 38 100 €. Ma note est passée de 100 à 51.
Garde une petite réserve chaque mois.
Toi, dans 3 ans"""

ALARMIST_LETTER = """Tu vas avoir des problèmes financiers : environ 8 000 € d'épargne,
10 500 € de crédit, une note de 51. Toi, dans 3 ans"""


def use_writer(writer):
    app.dependency_overrides[get_letter_writer] = lambda: writer


def teardown_function():
    app.dependency_overrides.pop(get_letter_writer, None)


# ---------- Les faits et la consigne ----------

def test_facts_come_from_the_engine():
    assert FACTS.years == 3
    assert FACTS.final_cash_with == 7978
    assert FACTS.turning_month == 32
    assert (FACTS.health_before, FACTS.health_after) == (100, 51)


def test_interpretation_is_decided_by_the_code():
    assert assess(FACTS).startswith("tendue mais sous contrôle")


def test_prompt_gives_rounded_amounts_and_signature():
    prompt = build_prompt(FACTS)
    for text in ["30 000 €", "8 000 €", "10 500 €", "mois 32", "100 aujourd'hui", "51 avec",
                 "Toi, dans 3 ans"]:
        assert text in prompt


def test_prompt_lists_previous_problems():
    assert "corrige-les" in build_prompt(FACTS, ["la note n'est pas citée"])


# ---------- La vérification ----------

def test_numbers_are_read_with_thousand_separators():
    assert numbers_in("environ 8 000 € et 10\u202f500 €") == [8000, 10500]


def test_good_letter_passes():
    assert check_letter(GOOD_LETTER, FACTS) == []


def test_missing_numbers_are_detected():
    problems = check_letter("Cher toi, tout va bien. Toi, dans 3 ans", FACTS)
    assert len(problems) == 3   # épargne, crédit et note manquants


def test_alarmist_tone_is_detected_when_savings_stay_positive():
    problems = check_letter(ALARMIST_LETTER, FACTS)
    assert any("alarmiste" in p for p in problems)


# ---------- La route ----------

def test_good_letter_is_accepted_at_first_try():
    calls = []
    use_writer(lambda system, prompt: calls.append(prompt) or GOOD_LETTER)
    body = client.post("/ai/future-letter", json=PAYLOAD).json()
    assert body["verified"] is True
    assert len(calls) == 1


def test_bad_letter_is_rewritten_once():
    calls = []

    def writer(system, prompt):
        calls.append(prompt)
        return ALARMIST_LETTER if len(calls) == 1 else GOOD_LETTER

    use_writer(writer)
    body = client.post("/ai/future-letter", json=PAYLOAD).json()
    assert len(calls) == 2
    assert "alarmiste" in calls[1]          # la 2e demande explique le défaut
    assert body["verified"] is True
    assert body["letter"] == GOOD_LETTER


def test_still_bad_letter_is_returned_with_its_problems():
    use_writer(lambda system, prompt: ALARMIST_LETTER)
    body = client.post("/ai/future-letter", json=PAYLOAD).json()
    assert body["verified"] is False
    assert body["problems"]


def test_ai_errors_become_502():
    def broken(system, prompt):
        raise RuntimeError("réseau coupé")

    use_writer(broken)
    assert client.post("/ai/future-letter", json=PAYLOAD).status_code == 502


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
    assert sent["body"]["options"]["temperature"] == 0.3
    assert [m["role"] for m in sent["body"]["messages"]] == ["system", "user"]