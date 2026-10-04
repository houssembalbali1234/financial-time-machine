from app.engine import Decision, FinancialProfile, health_score
from app.engine.health import scale

PROFILE = FinancialProfile(monthly_income=2800, monthly_expenses=1700, cash=15000,
                           annual_inflation=0.06)
CAR = Decision(name="Voiture", price=45000, down_payment=10000, loan_annual_rate=0.095,
               loan_months=60, asset_annual_depreciation=0.12, extra_monthly_cost=150)


def test_scale_is_bounded():
    assert scale(-5, 0, 6) == 0
    assert scale(3, 0, 6) == 50
    assert scale(10, 0, 6) == 100
    assert scale(0.20, 0.40, 0.0) == 50   # échelle inversée : moins c'est mieux


def test_score_is_between_0_and_100_with_four_factors():
    score = health_score(PROFILE)
    assert 0 <= score.total <= 100
    assert len(score.factors) == 4
    assert abs(sum(f.weight for f in score.factors) - 1) < 1e-9


def test_buying_the_car_lowers_the_score():
    assert health_score(PROFILE, CAR).total < health_score(PROFILE).total


def test_total_is_the_sum_of_points():
    score = health_score(PROFILE, CAR)
    assert abs(score.total - sum(f.points for f in score.factors)) <= 1


def test_very_healthy_profile_is_excellent():
    rich = FinancialProfile(monthly_income=6000, monthly_expenses=3000, cash=40000)
    score = health_score(rich)
    assert score.total == 100
    assert score.grade == "Excellente"


def test_overspending_profile_is_critical():
    broke = FinancialProfile(monthly_income=2000, monthly_expenses=2300, cash=500)
    assert health_score(broke).grade == "Critique"