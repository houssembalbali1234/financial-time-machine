"""Lettre du futur : Llama raconte la situation, le moteur fournit tous les chiffres."""
import re
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


def assess(facts: LetterFacts) -> str:
    """L'interprétation est décidée par le code, pas par l'IA : elle ne peut pas exagérer."""
    if facts.months_negative > 0:
        return "risquée : l'épargne passe sous zéro, il faudrait un découvert ou un autre crédit"
    if facts.health_after < 60:
        return "tendue mais sous contrôle : l'épargne reste positive, la marge de sécurité est faible"
    return "confortable : l'épargne reste positive avec une bonne marge de sécurité"


def money(value: float, step: int = 100) -> str:
    """Montant arrondi (à la centaine par défaut), écrit à la française : 7978 -> « 8 000 € »."""
    rounded = round(value / step) * step
    return f"{rounded:,.0f} €".replace(",", " ")


SYSTEM_PROMPT = """Tu écris une courte lettre en français, au tutoiement, signée par l'utilisateur
tel qu'il sera dans quelques années, adressée à lui-même aujourd'hui.

Plan obligatoire, en 3 paragraphes :
1. Où tu en es aujourd'hui, dans le futur : le projet réalisé, l'épargne atteinte et le crédit restant.
2. Ce que le projet a changé : la comparaison avec l'épargne sans le projet et l'évolution de la note.
3. Un conseil concret et bienveillant, tiré des chiffres. Puis la signature exacte demandée.

Règles strictes :
- Utilise les montants EXACTEMENT comme ils sont écrits dans la situation. N'invente aucun chiffre.
- Respecte l'interprétation donnée : ne la rends ni plus grave, ni plus rassurante.
- Ton calme et honnête. Pas d'ordre, pas de morale, ne dis pas d'abandonner le projet.
- 120 à 170 mots, sans titre ni liste. Ne recommande aucun produit financier."""


def build_prompt(facts: LetterFacts, problems: list[str] | None = None) -> str:
    """Décrit la situation à l'IA, avec des montants déjà arrondis et une interprétation fixée."""
    turning = (f"à partir du mois {facts.turning_month}, les dépenses dépassent les revenus chaque mois"
               if facts.turning_month else "les revenus restent supérieurs aux dépenses chaque mois")
    debt = (f"il reste {money(facts.debt_remaining)} de crédit à rembourser"
            if facts.debt_remaining > 0 else "le crédit est entièrement remboursé")
    prompt = f"""Situation :
- Projet : {facts.project_name}, prix {money(facts.price)}, réalisé maintenant.
- Dans {facts.years} ans, avec le projet : épargne de {money(facts.final_cash_with)} ; {debt}.
- Dans {facts.years} ans, sans le projet, l'épargne aurait été de {money(facts.final_cash_without)}.
- Trajectoire : {turning}.
- Note de santé financière sur 100 : {facts.health_before} aujourd'hui, {facts.health_after} avec le projet.
- Interprétation (à respecter) : situation {assess(facts)}.
- Signature exacte : « Toi, dans {facts.years} ans »

Écris la lettre."""
    if problems:
        prompt += ("\n\nTa version précédente avait ces défauts, corrige-les : "
                   + " ; ".join(problems) + ".")
    return prompt


# ---------- Vérification automatique de la lettre ----------

ALARMIST = ["problèmes financiers", "empirer", "catastroph", "faillite", "ruine", "abandonne", "jette"]


def numbers_in(text: str) -> list[float]:
    """Tous les nombres d'un texte, en tolérant les espaces des milliers : « 8 000 » -> 8000."""
    found = re.findall(r"\d{1,3}(?:[ \u00a0\u202f.]\d{3})+|\d+", text)
    return [float(re.sub(r"[ \u00a0\u202f.]", "", n)) for n in found]


def mentions(text: str, target: float) -> bool:
    """Le montant figure-t-il dans le texte, à l'arrondi près ?"""
    tolerance = max(150, abs(target) * 0.02)
    return any(abs(n - abs(target)) <= tolerance for n in numbers_in(text))


def check_letter(letter: str, facts: LetterFacts) -> list[str]:
    """Liste ce qui manque ou dérape dans la lettre. Liste vide = lettre validée."""
    problems = []
    if not mentions(letter, facts.final_cash_with):
        problems.append(f"l'épargne avec le projet ({money(facts.final_cash_with)}) n'est pas citée")
    if facts.debt_remaining > 0 and not mentions(letter, facts.debt_remaining):
        problems.append(f"le crédit restant ({money(facts.debt_remaining)}) n'est pas cité")
    if str(facts.health_after) not in re.findall(r"\d+", letter):
        problems.append(f"la note de santé avec le projet ({facts.health_after}) n'est pas citée")
    if f"dans {facts.years} an" not in letter.lower():
        problems.append(f"la signature « Toi, dans {facts.years} ans » manque")
    if facts.months_negative == 0:
        words = [w for w in ALARMIST if w in letter.lower()]
        if words:
            problems.append("le ton est trop alarmiste (" + ", ".join(words) + ") "
                            "alors que l'épargne reste positive")
    return problems