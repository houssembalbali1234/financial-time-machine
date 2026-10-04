"""Financial Health Score : note de 0 à 100, explicable facteur par facteur."""
from dataclasses import dataclass

from .models import Decision, FinancialProfile
from .projection import project

HORIZON = 12  # le score regarde les 12 prochains mois


@dataclass(frozen=True)
class HealthFactor:
    key: str
    label: str
    value: float        # la mesure brute (ex. 4.2 mois, 0.26 = 26 %)
    score: float        # note du facteur, de 0 à 100
    weight: float       # poids dans la note finale (somme = 1)
    explanation: str

    @property
    def points(self) -> float:
        """Points apportés à la note finale."""
        return round(self.score * self.weight, 1)


@dataclass(frozen=True)
class HealthScore:
    total: int
    grade: str
    factors: list[HealthFactor]


def scale(value: float, worst: float, best: float) -> float:
    """Transforme une mesure en note de 0 à 100 (linéaire entre worst et best)."""
    if best == worst:
        return 100.0
    ratio = (value - worst) / (best - worst)
    return round(100 * min(max(ratio, 0.0), 1.0), 1)


def grade_for(total: float) -> str:
    if total >= 80:
        return "Excellente"
    if total >= 60:
        return "Bonne"
    if total >= 40:
        return "Fragile"
    return "Critique"


def health_score(profile: FinancialProfile, decision: Decision | None = None) -> HealthScore:
    """Évalue la santé financière sur les 12 prochains mois, avec ou sans décision."""
    result = project(profile, HORIZON, decision)
    months = result.months

    # 1. Épargne de sécurité : combien de mois de sorties l'épargne couvre-t-elle ?
    cushion = result.min_cash / result.max_monthly_outflow if result.max_monthly_outflow else 0
    # 2. Endettement : part du revenu consacrée aux crédits
    debt = result.max_debt_ratio
    # 3. Capacité d'épargne : part du revenu qui reste chaque mois
    total_income = sum(m.income for m in months)
    savings_rate = sum(m.cash_flow for m in months) / total_income if total_income else -1
    # 4. Trajectoire : nombre de mois où l'on gagne plus qu'on ne dépense
    positive_months = sum(1 for m in months if m.cash_flow > 0)

    factors = [
        HealthFactor(
            "cushion", "Épargne de sécurité", round(cushion, 1),
            scale(cushion, 0, 6), 0.30,
            f"Votre épargne couvre {max(cushion, 0):.1f} mois de sorties (objectif : 6 mois).",
        ),
        HealthFactor(
            "debt", "Endettement", round(debt, 3),
            scale(debt, 0.40, 0.0), 0.25,
            f"Vos crédits représentent {debt:.0%} de votre revenu (limite : 40 %).",
        ),
        HealthFactor(
            "savings", "Capacité d'épargne", round(savings_rate, 3),
            scale(savings_rate, 0.0, 0.20), 0.25,
            f"Vous mettez de côté {max(savings_rate, 0):.0%} de votre revenu (objectif : 20 %).",
        ),
        HealthFactor(
            "trajectory", "Trajectoire", positive_months,
            0.0 if result.months_negative else scale(positive_months, 0, HORIZON), 0.20,
            f"{positive_months} mois sur {HORIZON} avec plus de rentrées que de sorties"
            + (" et un solde qui passe dans le rouge." if result.months_negative else "."),
        ),
    ]
    total = round(sum(f.score * f.weight for f in factors))
    return HealthScore(total=total, grade=grade_for(total), factors=factors)