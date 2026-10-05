"""Schémas Pydantic de l'historique des simulations."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.simulation import DecisionIn, Horizon, ProfileIn


class SaveRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    profile: ProfileIn
    decision: DecisionIn
    horizon_months: Horizon = 36


class SavedOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)   # lit directement un objet SQLAlchemy

    id: int
    name: str
    created_at: datetime
    profile: ProfileIn
    decision: DecisionIn
    horizon_months: int
    final_cash: float
    health_score: int