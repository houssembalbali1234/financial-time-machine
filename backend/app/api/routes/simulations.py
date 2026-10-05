"""Routes de simulation : relient l'API au moteur."""
from dataclasses import asdict

from fastapi import APIRouter

from app.engine import (Decision, ExistingLoan, FinancialProfile, IncomeShock,
                        SimulationResult, check_inputs, generate_purchase_scenarios,
                        months_of_resilience, project, run_stress_test)
from app.schemas.simulation import (DecisionIn, ProfileIn, ScenarioOut, ScenarioRequest,
                                    ScenariosResponse, SimulationRequest,
                                    SimulationResponse, StressRequest, StressResponse,
                                    SummaryOut)

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


def to_summary(result: SimulationResult) -> SummaryOut:
    """Extrait les chiffres clés d'une simulation."""
    return SummaryOut(
        final_cash=result.final.cash,
        final_net_worth=result.final.net_worth,
        final_debt=result.final.debt_remaining,
        min_cash=result.min_cash,
        months_negative=result.months_negative,
        first_negative_month=result.first_negative_month,
        max_debt_ratio=result.max_debt_ratio,
        max_monthly_outflow=result.max_monthly_outflow,
    )


SAFETY_MONTHS = 3        # épargne de sécurité : 3 mois de sorties
MAX_DEBT_RATIO = 0.40    # crédits : au plus 40 % du revenu


def is_safe(summary: SummaryOut) -> bool:
    """Sûr = l'épargne couvre toujours 3 mois de sorties (dépenses + crédits)
    et les crédits ne dépassent jamais 40 % du revenu."""
    cushion = SAFETY_MONTHS * summary.max_monthly_outflow
    return summary.min_cash >= cushion and summary.max_debt_ratio <= MAX_DEBT_RATIO


def pick_recommended(scenarios: list[ScenarioOut]) -> str:
    """Premier scénario sûr dans l'ordre de préférence de l'utilisateur.
    Si aucun n'est sûr, celui qui garde le plus d'épargne."""
    preference = ["maintenant", "moins_cher", "dans_6_mois", "dans_12_mois"]
    by_key = {s.key: s for s in scenarios}
    for key in preference:
        if is_safe(by_key[key].summary):
            return key
    return max(scenarios, key=lambda s: s.summary.min_cash).key


@router.post("", response_model=SimulationResponse)
def run_simulation(request: SimulationRequest) -> SimulationResponse:
    """Projette la situation financière mois par mois, avec ou sans décision."""
    profile = to_profile(request.profile)
    decision = to_decision(request.decision)
    result = project(profile, request.horizon_months, decision)
    return SimulationResponse(
        summary=to_summary(result),
        months=[asdict(m) for m in result.months],
        warnings=[asdict(w) for w in check_inputs(profile, decision)],
    )


@router.post("/scenarios", response_model=ScenariosResponse)
def compare_scenarios(request: ScenarioRequest) -> ScenariosResponse:
    """Compare : acheter maintenant, dans 6 mois, dans 12 mois, ou moins cher."""
    profile = to_profile(request.profile)
    variants = generate_purchase_scenarios(to_decision(request.decision))

    scenarios = []
    for key, decision in variants.items():
        result = project(profile, request.horizon_months, decision)
        scenarios.append(ScenarioOut(
            key=key,
            name=decision.name,
            price=decision.price,
            start_month=decision.start_month,
            summary=to_summary(result),
        ))

    return ScenariosResponse(
        scenarios=scenarios,
        recommended=pick_recommended(scenarios),
    )


@router.post("/stress-test", response_model=StressResponse)
def stress_test(request: StressRequest) -> StressResponse:
    """Compare la situation normale avec la situation après un choc de revenu."""
    profile = to_profile(request.profile)
    decision = to_decision(request.decision)
    shock = IncomeShock(**request.shock.model_dump())

    baseline = project(profile, request.horizon_months, decision)
    stressed = run_stress_test(profile, request.horizon_months, shock, decision)
    return StressResponse(
        baseline=to_summary(baseline),
        stressed=to_summary(stressed),
        cash_lost=round(baseline.final.cash - stressed.final.cash, 3),
        months_of_resilience=months_of_resilience(profile, decision),
    )