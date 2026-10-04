"""Schémas Pydantic du Financial Health Score."""
from pydantic import BaseModel

from app.schemas.simulation import DecisionIn, ProfileIn


class HealthScoreRequest(BaseModel):
    profile: ProfileIn
    decision: DecisionIn | None = None


class HealthFactorOut(BaseModel):
    key: str
    label: str
    value: float
    score: float
    weight: float
    points: float
    explanation: str


class HealthScoreOut(BaseModel):
    total: int
    grade: str
    factors: list[HealthFactorOut]


class HealthScoreResponse(BaseModel):
    current: HealthScoreOut
    after_decision: HealthScoreOut | None = None
    impact: int | None = None   # variation de la note causée par la décision