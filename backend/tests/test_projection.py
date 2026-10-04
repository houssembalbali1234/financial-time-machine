import pytest

from app.engine import (Decision, ExistingLoan, FinancialProfile, IncomeShock,
                        generate_purchase_scenarios, months_of_resilience, project,
                        run_stress_test)

# Profil de test : salarié à 2 800 TND, 1 700 TND de dépenses, 15 000 TND d'épargne
PROFILE = FinancialProfile(monthly_income=2_800, monthly_expenses=1_700, cash=15_000,
                           annual_inflation=0.06)

# Décision de test : voiture à 45 000 TND, 10 000 d'apport, crédit 60 mois à 9,5 %
CAR = Decision(name="Voiture", price=45_000, down_payment=10_000, loan_annual_rate=0.095,
               loan_months=60, asset_annual_depreciation=0.12, extra_monthly_cost=150)


def test_without_decision_cash_grows():
    # 500 TND d'économie par mois pendant 12 mois
    r = project(FinancialProfile(2_000, 1_500, 1_000), 12)
    assert r.final.cash == pytest.approx(1_000 + 12 * 500)
    assert r.months_negative == 0


def test_inflation_increases_expenses():
    # Au 13e mois, les dépenses ont pris 6 %
    r = project(PROFILE, 24)
    assert r.months[12].expenses == pytest.approx(1_700 * 1.06, rel=1e-6)


def test_purchase_creates_debt_asset_and_reduces_cash():
    base = project(PROFILE, 36)
    with_car = project(PROFILE, 36, CAR)
    assert with_car.months[0].debt_remaining > 0
    assert with_car.months[0].asset_value == pytest.approx(45_000)
    assert with_car.final.cash < base.final.cash
    assert 0 < with_car.max_debt_ratio < 0.4


def test_delayed_purchase_has_no_debt_before_start():
    later = generate_purchase_scenarios(CAR)["dans_6_mois"]
    r = project(PROFILE, 24, later)
    assert all(m.debt_remaining == 0 for m in r.months[:6])
    assert r.months[6].debt_remaining > 0


def test_scenarios_are_generated():
    s = generate_purchase_scenarios(CAR)
    assert set(s) == {"maintenant", "dans_6_mois", "dans_12_mois", "moins_cher"}
    assert s["moins_cher"].price == pytest.approx(36_000)


def test_existing_loan_is_repaid():
    # Un crédit de 12 mois en cours doit être soldé après le 12e mois
    p = FinancialProfile(3_000, 1_500, 5_000, existing_loans=(ExistingLoan(6_000, 0.1, 12),))
    r = project(p, 24)
    assert r.months[11].debt_remaining == 0
    assert r.months[12].loan_payments == 0


def test_income_shock_reduces_cash():
    # 3 mois sans revenu = exactement 3 salaires en moins
    shock = IncomeShock("perte_emploi", 0.0, 1, 3)
    stressed = run_stress_test(PROFILE, 12, shock, CAR)
    normal = project(PROFILE, 12, CAR)
    assert stressed.final.cash == pytest.approx(normal.final.cash - 3 * 2_800, abs=0.01)


def test_months_of_resilience():
    # 9 000 TND d'épargne, 1 500 TND de dépenses, pas d'inflation -> 6 mois
    assert months_of_resilience(FinancialProfile(2_000, 1_500, 9_000)) == 6


def test_invalid_horizon():
    with pytest.raises(ValueError):
        project(PROFILE, 0)





def test_debt_ratio_without_income_is_capped():
    shock = IncomeShock("perte_emploi", 0.0, 1, 3)
    r = run_stress_test(PROFILE, 12, shock, CAR)
    assert r.months[0].debt_ratio == 1.0


def test_resilience_is_shorter_with_a_loan():
    assert months_of_resilience(PROFILE, CAR) < months_of_resilience(PROFILE)