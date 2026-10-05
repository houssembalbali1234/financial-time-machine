"""Avertissements : repère les saisies risquées ou incohérentes avant même la simulation."""
from dataclasses import dataclass, field

from .loans import monthly_payment
from .models import Decision, FinancialProfile

SAFETY_MONTHS = 3        # épargne de sécurité conseillée : 3 mois de dépenses
MAX_DEBT_RATIO = 0.40    # crédits : au plus 40 % du revenu
MAX_EXTRA_COST = 0.30    # frais liés à l'achat : au plus 30 % du revenu


@dataclass(frozen=True)
class InputWarning:
    code: str                    # identifiant stable, traduit en message par le frontend
    level: str                   # "danger" (bloquant) ou "attention" (à vérifier)
    values: dict[str, float] = field(default_factory=dict)


def check_inputs(profile: FinancialProfile,
                 decision: Decision | None = None) -> list[InputWarning]:
    """Liste les problèmes détectés dans le profil et la décision, du plus grave au moins grave."""
    warnings: list[InputWarning] = []
    income = profile.monthly_income

    if profile.monthly_expenses >= income:
        warnings.append(InputWarning("expenses_exceed_income", "danger", {
            "expenses": profile.monthly_expenses, "income": income,
        }))

    if decision is None:
        return warnings

    remaining = profile.cash - decision.down_payment
    if remaining < 0:
        warnings.append(InputWarning("down_payment_exceeds_cash", "danger", {
            "down_payment": decision.down_payment, "cash": profile.cash, "missing": -remaining,
        }))
    elif remaining < SAFETY_MONTHS * profile.monthly_expenses:
        warnings.append(InputWarning("low_cushion_after_down_payment", "attention", {
            "remaining": remaining, "target": SAFETY_MONTHS * profile.monthly_expenses,
        }))

    payments = monthly_payment(decision.loan_amount, decision.loan_annual_rate,
                               decision.loan_months)
    payments += sum(monthly_payment(l.remaining_principal, l.annual_rate, l.remaining_months)
                    for l in profile.existing_loans)
    if income > 0 and payments / income > MAX_DEBT_RATIO:
        warnings.append(InputWarning("high_debt_ratio", "danger", {
            "payments": round(payments, 2), "ratio": round(payments / income, 4),
        }))

    if income > 0 and decision.extra_monthly_cost > MAX_EXTRA_COST * income:
        warnings.append(InputWarning("high_extra_cost", "attention", {
            "extra_cost": decision.extra_monthly_cost,
            "ratio": round(decision.extra_monthly_cost / income, 4),
        }))

    order = {"danger": 0, "attention": 1}
    return sorted(warnings, key=lambda w: order[w.level])