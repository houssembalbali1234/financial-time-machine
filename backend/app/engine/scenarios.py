"""Génération automatique de scénarios alternatifs pour une décision d'achat."""
from dataclasses import replace

from .models import Decision


def generate_purchase_scenarios(decision: Decision, cheaper_ratio: float = 0.8) -> dict[str, Decision]:
    """Maintenant, dans 6 mois, dans 12 mois, et une option moins chère."""
    cheaper_price = decision.price * cheaper_ratio
    down_share = decision.down_payment / decision.price if decision.price else 0
    return {
        "maintenant": decision,
        "dans_6_mois": replace(decision, start_month=decision.start_month + 6),
        "dans_12_mois": replace(decision, start_month=decision.start_month + 12),
        "moins_cher": replace(
            decision,
            name=f"{decision.name} (option moins chère)",
            price=cheaper_price,
            down_payment=cheaper_price * down_share,
        ),
    }