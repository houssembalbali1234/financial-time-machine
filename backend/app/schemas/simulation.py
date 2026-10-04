"""Schémas Pydantic : forme des données reçues et renvoyées par l'API de simulation."""
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ExistingLoanIn(BaseModel):
    remaining_principal: float = Field(gt=0, description="Capital restant dû")
    annual_rate: float = Field(ge=0, le=1, description="Taux annuel (0.095 = 9,5 %)")
    remaining_months: int = Field(gt=0, le=360)


class ProfileIn(BaseModel):
    monthly_income: float = Field(ge=0, description="Revenu mensuel net")
    monthly_expenses: float = Field(ge=0, description="Dépenses mensuelles")
    cash: float = Field(description="Épargne disponible")
    annual_inflation: float = Field(default=0.0, ge=0, le=1)
    annual_income_growth: float = Field(default=0.0, ge=-1, le=1)
    existing_loans: list[ExistingLoanIn] = Field(default_factory=list)


class DecisionIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    down_payment: float = Field(ge=0, description="Apport personnel")
    loan_annual_rate: float = Field(ge=0, le=1)
    loan_months: int = Field(ge=1, le=360)
    start_month: int = Field(default=1, ge=1, le=60)
    asset_annual_depreciation: float = Field(default=0.0, ge=0, le=1)
    extra_monthly_cost: float = Field(default=0.0, ge=0)

    @model_validator(mode="after")
    def check_down_payment(self) -> "DecisionIn":
        if self.down_payment > self.price:
            raise ValueError("L'apport ne peut pas dépasser le prix")
        return self


class SimulationRequest(BaseModel):
    profile: ProfileIn
    decision: DecisionIn | None = None
    horizon_months: Literal[6, 12, 24, 36, 60] = 36

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "profile": {
                    "monthly_income": 2800,
                    "monthly_expenses": 1700,
                    "cash": 15000,
                    "annual_inflation": 0.06,
                },
                "decision": {
                    "name": "Voiture",
                    "price": 45000,
                    "down_payment": 10000,
                    "loan_annual_rate": 0.095,
                    "loan_months": 60,
                    "asset_annual_depreciation": 0.12,
                    "extra_monthly_cost": 150,
                },
                "horizon_months": 36,
            }]
        }
    }


class MonthOut(BaseModel):
    month: int
    income: float
    expenses: float
    loan_payments: float
    cash_flow: float
    cash: float
    debt_remaining: float
    asset_value: float
    net_worth: float
    debt_ratio: float


class SummaryOut(BaseModel):
    final_cash: float
    final_net_worth: float
    final_debt: float
    min_cash: float
    months_negative: int
    first_negative_month: int | None
    max_debt_ratio: float
    max_monthly_outflow: float


class SimulationResponse(BaseModel):
    summary: SummaryOut
    months: list[MonthOut]


class ScenarioRequest(BaseModel):
    profile: ProfileIn
    decision: DecisionIn
    horizon_months: Literal[6, 12, 24, 36, 60] = 36


class ScenarioOut(BaseModel):
    key: str
    name: str
    price: float
    start_month: int
    summary: SummaryOut


class ScenariosResponse(BaseModel):
    scenarios: list[ScenarioOut]
    recommended: str


class ShockIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    income_factor: float = Field(ge=0, le=1, description="0.7 = revenu -30 %, 0 = perte totale")
    start_month: int = Field(default=1, ge=1, le=60)
    duration_months: int = Field(ge=1, le=60)


class StressRequest(BaseModel):
    profile: ProfileIn
    decision: DecisionIn | None = None
    shock: ShockIn
    horizon_months: Literal[6, 12, 24, 36, 60] = 36


class StressResponse(BaseModel):
    baseline: SummaryOut
    stressed: SummaryOut
    cash_lost: float
    months_of_resilience: int