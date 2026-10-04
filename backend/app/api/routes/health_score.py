"""Route du Financial Health Score."""
from fastapi import APIRouter

from app.api.routes.simulations import to_decision, to_profile
from app.engine import HealthScore, health_score
from app.schemas.health import (HealthFactorOut, HealthScoreOut, HealthScoreRequest,
                                HealthScoreResponse)

router = APIRouter(prefix="/health-score", tags=["Health Score"])


def to_score_out(score: HealthScore) -> HealthScoreOut:
    """Convertit le score du moteur en réponse JSON."""
    return HealthScoreOut(
        total=score.total,
        grade=score.grade,
        factors=[
            HealthFactorOut(
                key=f.key,
                label=f.label,
                value=f.value,
                score=f.score,
                weight=f.weight,
                points=f.points,
                explanation=f.explanation,
            )
            for f in score.factors
        ],
    )


@router.post("", response_model=HealthScoreResponse)
def get_health_score(request: HealthScoreRequest) -> HealthScoreResponse:
    """Note de santé financière actuelle et, si une décision est fournie, après celle-ci."""
    profile = to_profile(request.profile)
    current = health_score(profile)

    if request.decision is None:
        return HealthScoreResponse(current=to_score_out(current))

    after = health_score(profile, to_decision(request.decision))
    return HealthScoreResponse(
        current=to_score_out(current),
        after_decision=to_score_out(after),
        impact=after.total - current.total,
    )