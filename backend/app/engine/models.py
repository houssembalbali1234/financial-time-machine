from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExistingLoan:
    """Crédit déjà en cours au moment de la simulation."""
    remaining_principal: float
    annual_rate: float          # ex. 0.095 pour 9,5 % (TMM + marge)
    remaining_months: int


@dataclass(frozen=True)
class FinancialProfile:
    """Situation financière de départ (montants mensuels en TND)."""
    monthly_income: float
    monthly_expenses: float
    cash: float                              # épargne disponible
    annual_inflation: float = 0.0            # appliquée aux dépenses
    annual_income_growth: float = 0.0
    existing_loans: tuple[ExistingLoan, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Decision:
    """Décision d'achat financée (en partie) par un crédit."""
    name: str
    price: float
    down_payment: float
    loan_annual_rate: float
    loan_months: int
    start_month: int = 1                     # mois de l'achat (1 = mois prochain)
    asset_annual_depreciation: float = 0.0   # ex. 0.12 pour une voiture
    extra_monthly_cost: float = 0.0          # assurance, entretien, carburant...

    @property
    def loan_amount(self) -> float:
        return max(self.price - self.down_payment, 0.0)


@dataclass(frozen=True)
class MonthResult:
    month: int
    income: float
    expenses: float
    loan_payments: float
    cash_flow: float
    cash: float
    debt_remaining: float
    asset_value: float
    net_worth: float
    debt_ratio: float           # mensualités / revenu


@dataclass(frozen=True)
class SimulationResult:
    months: list[MonthResult]

    @property
    def final(self) -> MonthResult:
        return self.months[-1]

    @property
    def min_cash(self) -> float:
        return min(m.cash for m in self.months)

    @property
    def months_negative(self) -> int:
        return sum(1 for m in self.months if m.cash < 0)

    @property
    def max_debt_ratio(self) -> float:
        return max(m.debt_ratio for m in self.months)

    @property
    def first_negative_month(self) -> int | None:
        return next((m.month for m in self.months if m.cash < 0), None)