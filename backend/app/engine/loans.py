"""Calculs de crédit : mensualité constante et amortissement."""
from dataclasses import dataclass


def monthly_payment(principal: float, annual_rate: float, months: int) -> float:
    """Mensualité constante d'un prêt amortissable."""
    if principal <= 0 or months <= 0:
        return 0.0
    r = annual_rate / 12
    if r == 0:
        return principal / months
    return principal * r / (1 - (1 + r) ** -months)


@dataclass
class LoanState:
    """État d'un prêt qui avance mois par mois."""
    balance: float
    annual_rate: float
    remaining_months: int

    def __post_init__(self) -> None:
        self.payment = monthly_payment(self.balance, self.annual_rate, self.remaining_months)

    def step(self) -> float:
        """Avance d'un mois et renvoie la mensualité payée."""
        if self.remaining_months <= 0 or self.balance <= 1e-9:
            return 0.0
        interest = self.balance * self.annual_rate / 12
        payment = min(self.payment, self.balance + interest)
        self.balance = self.balance + interest - payment
        self.remaining_months -= 1
        if self.remaining_months == 0:
            self.balance = 0.0
        return payment

    def set_rate(self, new_annual_rate: float) -> None:
        """Taux variable (TMM) : recalcule la mensualité sur le capital restant."""
        self.annual_rate = new_annual_rate
        self.payment = monthly_payment(self.balance, new_annual_rate, self.remaining_months)


def amortization_schedule(principal: float, annual_rate: float, months: int) -> list[dict]:
    """Tableau d'amortissement complet, mois par mois."""
    loan = LoanState(principal, annual_rate, months)
    rows = []
    for m in range(1, months + 1):
        start = loan.balance
        payment = loan.step()
        rows.append({
            "month": m,
            "payment": round(payment, 3),
            "interest": round(start * annual_rate / 12, 3),
            "principal": round(start - loan.balance, 3),
            "balance": round(loan.balance, 3),
        })
    return rows