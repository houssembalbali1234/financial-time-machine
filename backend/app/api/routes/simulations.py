"""Routes de simulation : relient l'API au moteur."""
from dataclasses import asdict

from fastapi import APIRouter

from app.engine import (Decision, ExistingLoan, FinancialProfile, SimulationResult,
                        project)
from app.schemas.simulation import (DecisionIn, ProfileIn, SimulationRequest,
                                    SimulationResponse)

router = APIRouter(prefix="/simulations", tags=["Simulations"])


def to_profile(p: ProfileIn) -> FinancialProfile:
    """Convertit le profil reçu par l'API en objet du moteur."""
    return FinancialProfile(
        monthly_income=p.monthly_income,
        monthly_expenses=p.monthly_expenses,
        cash=p.cash,
        annual_inflation=p.annual_inflation,
        annual_income_growth=p.annual_income_growth,
        existing_loans=tuple(ExistingLoan(**loan.model_dump()) for loan in p.existing_loans),
    )


def to_decision(d: DecisionIn | None) -> Decision | None:
    """Convertit la décision reçue par l'API en objet du moteur."""
    return Decision(**d.model_dump()) if d else None


def to_response(result: SimulationResult) -> SimulationResponse:
    """Transforme le résultat du moteur en réponse JSON."""
    return SimulationResponse(
        summary={
            "final_cash": result.final.cash,
            "final_net_worth": result.final.net_worth,
            "final_debt": result.final.debt_remaining,
            "min_cash": result.min_cash,
            "months_negative": result.months_negative,
            "first_negative_month": result.first_negative_month,
            "max_debt_ratio": result.max_debt_ratio,
        },
        months=[asdict(m) for m in result.months],
    )


@router.post("", response_model=SimulationResponse)
def run_simulation(request: SimulationRequest) -> SimulationResponse:
    """Projette la situation financière mois par mois, avec ou sans décision."""
    result = project(
        to_profile(request.profile),
        request.horizon_months,
        to_decision(request.decision),
    )
    return to_response(result)