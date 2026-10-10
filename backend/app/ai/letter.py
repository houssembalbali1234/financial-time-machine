"""Lettre du futur : Llama raconte la situation, le moteur fournit tous les chiffres."""
from dataclasses import dataclass

from app.engine import Decision, FinancialProfile, health_score, project


@dataclass(frozen=True)
class LetterFacts:
    """Les seuls chiffres que l'IA a le droit d'utiliser, tous calculés par le moteur."""
    project_name: str
    price: float
    years: int
    final_cash_with: float
    final_cash_without: float
    debt_remaining: float
    turning_month: int | None          # premier mois où l'on dépense plus qu'on ne gagne
    months_negative: int               # mois avec une épargne négative
    health_before: int
    health_after: int


def build_facts(profile: FinancialProfile, decision: Decision, horizon_months: int) -> LetterFacts:
    with_project = project(profile, horizon_months, decision)
    without_project = project(profile, horizon_months)
    return LetterFacts(
        project_name=decision.name,
        price=decision.price,
        years=horizon_months // 12,
        final_cash_with=round(with_project.final.cash),
        final_cash_without=round(without_project.final.cash),
        debt_remaining=round(with_project.final.debt_remaining),
        turning_month=next((m.month for m in with_project.months if m.cash_flow < 0), None),
        months_negative=with_project.months_negative,
        health_before=health_score(profile).total,
        health_after=health_score(profile, decision).total,
    )


SYSTEM_PROMPT = """Tu écris une courte lettre en français, signée par l'utilisateur lui-même,
tel qu'il sera dans quelques années, adressée à lui-même aujourd'hui.

Règles strictes :
- Utilise UNIQUEMENT les chiffres fournis. N'invente aucun montant, aucune date, aucun événement chiffré.
- Arrondis les montants à la centaine et écris-les en euros (ex. « environ 7 900 € »).
- Ton chaleureux, honnête et concret, ni alarmiste ni moralisateur. Tutoiement.
- 120 à 180 mots, en 2 ou 3 paragraphes, sans titre ni liste.
- Termine par un conseil concret tiré des chiffres, puis signe « Toi, dans N ans ».
- Ce n'est pas un conseil financier professionnel : ne recommande aucun produit financier."""


def build_prompt(facts: LetterFacts) -> str:
    """Décrit la situation à l'IA, chiffre par chiffre."""
    turning = (f"à partir du mois {facts.turning_month}, les dépenses dépassent les revenus chaque mois"
               if facts.turning_month else "les revenus restent supérieurs aux dépenses chaque mois")
    negative = (f"l'épargne passe sous zéro pendant {facts.months_negative} mois"
                if facts.months_negative else "l'épargne ne passe jamais sous zéro")
    return f"""Projet : {facts.project_name}, prix {facts.price:.0f} €.
Horizon : dans {facts.years} ans.
Épargne dans {facts.years} ans avec le projet : {facts.final_cash_with:.0f} €.
Épargne dans {facts.years} ans sans le projet : {facts.final_cash_without:.0f} €.
Crédit restant à rembourser à ce moment-là : {facts.debt_remaining:.0f} €.
Trajectoire : {turning} ; {negative}.
Santé financière (note sur 100) : {facts.health_before} aujourd'hui, {facts.health_after} après le projet.

Écris la lettre."""