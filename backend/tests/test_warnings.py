from app.engine import Decision, FinancialProfile, check_inputs

PROFILE = FinancialProfile(monthly_income=2500, monthly_expenses=1700, cash=12000)
CAR = Decision(name="Voiture", price=25000, down_payment=5000, loan_annual_rate=0.065,
               loan_months=60, asset_annual_depreciation=0.12, extra_monthly_cost=200)


def codes(warnings):
    return [w.code for w in warnings]


def test_reasonable_purchase_has_no_warning():
    assert check_inputs(PROFILE, CAR) == []


def test_down_payment_above_savings_is_dangerous():
    w = check_inputs(PROFILE, Decision("Logement", 250000, 50000, 0.037, 300))
    assert "down_payment_exceeds_cash" in codes(w)
    missing = next(x for x in w if x.code == "down_payment_exceeds_cash").values["missing"]
    assert missing == 38000


def test_emptying_savings_triggers_attention():
    all_in = Decision("Voiture", 18000, 12000, 0.052, 108)
    w = check_inputs(PROFILE, all_in)
    assert codes(w) == ["low_cushion_after_down_payment"]
    assert w[0].level == "attention"


def test_heavy_loan_is_flagged():
    house = Decision("Logement", 250000, 10000, 0.037, 300)
    assert "high_debt_ratio" in codes(check_inputs(PROFILE, house))


def test_huge_monthly_costs_are_flagged():
    costly = Decision("Voiture", 18000, 2000, 0.052, 108, extra_monthly_cost=2000)
    assert "high_extra_cost" in codes(check_inputs(PROFILE, costly))


def test_dangers_come_first():
    bad = Decision("Logement", 250000, 50000, 0.037, 300, extra_monthly_cost=2000)
    levels = [w.level for w in check_inputs(PROFILE, bad)]
    assert levels == sorted(levels, key=lambda l: l != "danger")


def test_spending_more_than_earning_is_flagged_without_decision():
    broke = FinancialProfile(monthly_income=2000, monthly_expenses=2300, cash=500)
    assert codes(check_inputs(broke)) == ["expenses_exceed_income"]