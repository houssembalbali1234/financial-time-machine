import pytest

from app.engine.loans import LoanState, amortization_schedule, monthly_payment


def test_monthly_payment_known_value():
    # 40 000 TND sur 60 mois à 9 % : mensualité de référence ≈ 830,33
    assert monthly_payment(40_000, 0.09, 60) == pytest.approx(830.33, abs=0.01)


def test_zero_rate_is_linear():
    # Sans intérêts, 12 000 sur 12 mois = 1 000 par mois
    assert monthly_payment(12_000, 0.0, 12) == pytest.approx(1_000)


def test_schedule_ends_at_zero_and_repays_principal():
    rows = amortization_schedule(40_000, 0.09, 60)
    assert len(rows) == 60
    assert rows[-1]["balance"] == 0
    assert sum(r["principal"] for r in rows) == pytest.approx(40_000, abs=0.5)


def test_rate_increase_raises_payment():
    # Si le taux variable monte, la mensualité doit augmenter
    loan = LoanState(30_000, 0.08, 48)
    before = loan.payment
    loan.step()
    loan.set_rate(0.10)
    assert loan.payment > before