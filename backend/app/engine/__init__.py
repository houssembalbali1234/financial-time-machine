"""Moteur de simulation financière : Python pur, déterministe, sans dépendance web."""
from .models import Decision, ExistingLoan, FinancialProfile, MonthResult, SimulationResult
from .projection import project
from .scenarios import generate_purchase_scenarios
from .stress import IncomeShock, months_of_resilience, run_stress_test

__all__ = [
    "Decision", "ExistingLoan", "FinancialProfile", "MonthResult", "SimulationResult",
    "project", "generate_purchase_scenarios", "IncomeShock", "run_stress_test",
    "months_of_resilience",
]