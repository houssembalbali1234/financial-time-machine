"""Schémas Pydantic des fonctions d'IA."""
from typing import Literal

from pydantic import BaseModel, Field

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


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=2000)


class AskRequest(BaseModel):
    profile: ProfileIn
    decision: DecisionIn
    horizon_months: Horizon = 36
    question: str = Field(min_length=2, max_length=500)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)


class AskResponse(BaseModel):
    answer: str
    verified: bool      # False si la réponse contient un montant absent de la simulation