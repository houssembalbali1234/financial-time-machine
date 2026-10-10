"""Schémas Pydantic des fonctions d'IA."""
from pydantic import BaseModel

from app.schemas.simulation import DecisionIn, Horizon, ProfileIn


class LetterRequest(BaseModel):
    profile: ProfileIn
    decision: DecisionIn
    horizon_months: Horizon = 36


class LetterResponse(BaseModel):
    letter: str
    verified: bool          # True si la lettre a passé toutes les vérifications
    problems: list[str]     # ce qui reste à corriger si verified est False
    facts: dict             # les chiffres utilisés, pour que l'utilisateur puisse les vérifier