"""Stress tests : chocs de revenus et de taux."""
from dataclasses import dataclass

from .models import Decision, FinancialProfile, SimulationResult
from .projection import project


@dataclass(frozen=True)
class IncomeShock:
    name: str
    income_factor: float      # 0.7 = -30 %, 0.0 = perte totale
    start_month: int
    duration_months: int


def run_stress_test(profile: FinancialProfile, horizon_months: int, shock: IncomeShock,
                    decision: Decision | None = None) -> SimulationResult:
    """Rejoue la projection en appliquant un choc de revenu sur une période."""
    multipliers = {
        m: shock.income_factor
        for m in range(shock.start_month, shock.start_month + shock.duration_months)
    }
    return project(profile, horizon_months, decision, income_multipliers=multipliers)


def months_of_resilience(profile: FinancialProfile, decision: Decision | None = None,
                         max_months: int = 60) -> int:
    """Nombre de mois tenus sans aucun revenu avant que l'épargne devienne négative."""
    shock = IncomeShock("perte_totale", 0.0, 1, max_months)
    result = run_stress_test(profile, max_months, shock, decision)
    first_negative = result.first_negative_month
    return max_months if first_negative is None else first_negative - 1