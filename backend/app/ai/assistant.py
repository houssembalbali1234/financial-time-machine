"""Assistant financier : Llama répond aux questions, mais seulement avec les chiffres du moteur."""
from app.ai.letter import mentions, money, numbers_in
from app.engine import (Decision, FinancialProfile, IncomeShock, generate_purchase_scenarios,
                        health_score, months_of_resilience, project, run_stress_test)

SCENARIO_LABELS = {
    "maintenant": "acheter maintenant",
    "moins_cher": "acheter 20 % moins cher",
    "dans_6_mois": "attendre 6 mois",
    "dans_12_mois": "attendre 12 mois",
}


def build_context(profile: FinancialProfile, decision: Decision,
                  horizon_months: int) -> tuple[str, list[float]]:
    """Calcule tout ce que l'assistant peut dire, et la liste des chiffres autorisés."""
    years = horizon_months // 12
    with_project = project(profile, horizon_months, decision)
    without_project = project(profile, horizon_months)
    health_now, health_after = health_score(profile), health_score(profile, decision)
    months = with_project.months
    monthly_saving = sum(m.cash_flow for m in months[:12]) / min(12, len(months))
    payment = months[0].loan_payments
    job_loss = run_stress_test(profile, horizon_months, IncomeShock("perte", 0.0, 1, 3), decision)

    lines = [
        f"Revenu mensuel : {money(profile.monthly_income, 10)}. "
        f"Dépenses mensuelles : {money(profile.monthly_expenses, 10)}. "
        f"Épargne actuelle : {money(profile.cash)}.",
        f"Projet : {decision.name}, prix {money(decision.price)}, apport {money(decision.down_payment)}, "
        f"mensualité de crédit {money(payment, 10)} pendant {decision.loan_months} mois.",
        f"Dans {years} ans : épargne de {money(with_project.final.cash)} avec le projet, "
        f"{money(without_project.final.cash)} sans ; crédit restant {money(with_project.final.debt_remaining)}.",
        f"Épargne mise de côté en moyenne la première année avec le projet : {money(monthly_saving, 10)} par mois.",
        f"Note de santé financière : {health_now.total}/100 aujourd'hui, {health_after.total}/100 avec le projet.",
        "Détail de la note avec le projet : "
        + " ; ".join(f"{f.label} {f.points:.0f}/{f.weight * 100:.0f}" for f in health_after.factors) + ".",
        f"En cas de perte d'emploi de 3 mois juste après le projet : épargne au plus bas "
        f"{money(job_loss.min_cash)} ; sans aucun revenu, l'épargne tiendrait "
        f"{months_of_resilience(profile, decision)} mois.",
    ]
    for key, variant in generate_purchase_scenarios(decision).items():
        result = project(profile, horizon_months, variant)
        lines.append(f"Scénario « {SCENARIO_LABELS[key]} » (prix {money(variant.price)}) : épargne au plus bas "
                     f"{money(result.min_cash)}, épargne dans {years} ans {money(result.final.cash)}.")

    context = "\n".join(f"- {line}" for line in lines)
    return context, numbers_in(context)


SYSTEM_PROMPT = """Tu es l'assistant de Financial Time Machine, un simulateur financier éducatif.
Tu réponds en français, au vouvoiement, en 2 à 5 phrases simples.

Règles strictes :
- Réponds UNIQUEMENT à partir des chiffres de la situation fournie. N'invente aucun chiffre et ne fais
  aucun nouveau calcul : si la réponse n'y figure pas, dis-le simplement et propose de modifier la
  simulation (prix, apport, durée, etc.) pour la voir.
- Recopie les montants exactement comme ils sont écrits.
- Reste neutre et bienveillant : tu éclaires la décision, tu ne la prends pas à la place de l'utilisateur.
- Ne recommande aucun produit financier, aucune banque, aucun placement.
- Si la question n'a rien à voir avec la situation financière de l'utilisateur, réponds poliment
  que tu ne peux aider que sur cette simulation."""


def build_messages(context: str, question: str, history: list[dict]) -> list[dict]:
    """La situation, les derniers échanges, puis la nouvelle question."""
    messages = [{"role": "system", "content": f"{SYSTEM_PROMPT}\n\nSituation de l'utilisateur :\n{context}"}]
    messages += history[-6:]                    # les 3 derniers échanges suffisent
    messages.append({"role": "user", "content": question})
    return messages


def invented_numbers(answer: str, allowed: list[float]) -> list[float]:
    """Les montants de la réponse qui ne viennent pas de la situation (les petits nombres sont tolérés)."""
    return [n for n in numbers_in(answer)
            if n > 120 and not any(mentions(f"{a:.0f}", n) for a in allowed)]