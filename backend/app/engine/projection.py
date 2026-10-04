"""Projection mois par mois de la situation financière."""
from .loans import LoanState
from .models import Decision, FinancialProfile, MonthResult, SimulationResult


def debt_ratio(payments: float, income: float) -> float:
    """Part du revenu consacrée aux crédits (plafonnée à 1 si le revenu est nul)."""
    if income > 0:
        return round(payments / income, 4)
    return 1.0 if payments > 0 else 0.0


def project(
    profile: FinancialProfile,
    horizon_months: int,
    decision: Decision | None = None,
    income_multipliers: dict[int, float] | None = None,
    rate_shift_from: tuple[int, float] | None = None,
) -> SimulationResult:
    """Projette la situation sur `horizon_months` mois.

    income_multipliers : {mois: facteur} pour simuler un choc (0.7 = revenu -30 %).
    rate_shift_from    : (mois, +delta) hausse du taux variable des crédits à partir d'un mois.
    """
    if horizon_months <= 0:
        raise ValueError("horizon_months doit être > 0")
    income_multipliers = income_multipliers or {}

    loans = [LoanState(l.remaining_principal, l.annual_rate, l.remaining_months)
             for l in profile.existing_loans]
    cash = profile.cash
    asset_value = 0.0
    bought = False
    results: list[MonthResult] = []

    for m in range(1, horizon_months + 1):
        # 1. Revenus et dépenses du mois (avec croissance et inflation)
        years = (m - 1) / 12
        income = profile.monthly_income * (1 + profile.annual_income_growth) ** years
        income *= income_multipliers.get(m, 1.0)
        expenses = profile.monthly_expenses * (1 + profile.annual_inflation) ** years

        # 2. Le mois de l'achat : on paie l'apport et on ouvre le crédit
        if decision and m == decision.start_month:
            cash -= decision.down_payment
            asset_value = decision.price
            if decision.loan_amount > 0:
                loans.append(LoanState(decision.loan_amount, decision.loan_annual_rate,
                                       decision.loan_months))
            bought = True

        # 3. Après l'achat : coûts d'usage et dépréciation du bien
        if bought and decision:
            expenses += decision.extra_monthly_cost
            if m > decision.start_month:
                asset_value *= (1 - decision.asset_annual_depreciation) ** (1 / 12)

        # 4. Hausse éventuelle du taux variable (TMM)
        if rate_shift_from and m == rate_shift_from[0]:
            for loan in loans:
                loan.set_rate(loan.annual_rate + rate_shift_from[1])

        # 5. Paiement des mensualités et mise à jour du solde
        payments = sum(loan.step() for loan in loans)
        cash_flow = income - expenses - payments
        cash += cash_flow
        debt = sum(loan.balance for loan in loans)

        results.append(MonthResult(
            month=m,
            income=round(income, 3),
            expenses=round(expenses, 3),
            loan_payments=round(payments, 3),
            cash_flow=round(cash_flow, 3),
            cash=round(cash, 3),
            debt_remaining=round(debt, 3),
            asset_value=round(asset_value, 3),
            net_worth=round(cash + asset_value - debt, 3),
            debt_ratio=debt_ratio(payments, income),
        ))

    return SimulationResult(results)