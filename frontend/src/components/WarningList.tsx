import type { InputWarning } from "@/lib/api";
import { formatMoney } from "@/lib/format";

const percent = (ratio: number) => `${Math.round(ratio * 100)} %`;

// Le backend renvoie un code et des valeurs ; le texte est écrit ici, dans la langue de l'interface.
function message(w: InputWarning): string {
  const v = w.values;
  switch (w.code) {
    case "expenses_exceed_income":
      return `Vos dépenses (${formatMoney(v.expenses)}) dépassent déjà votre revenu `
        + `(${formatMoney(v.income)}), avant même ce projet.`;
    case "down_payment_exceeds_cash":
      return `Votre apport (${formatMoney(v.down_payment)}) dépasse votre épargne `
        + `(${formatMoney(v.cash)}) : il vous manque ${formatMoney(v.missing)}.`;
    case "low_cushion_after_down_payment":
      return `Après l'apport, il ne vous resterait que ${formatMoney(v.remaining)} d'épargne. `
        + `Gardez au moins ${formatMoney(v.target)}, soit 3 mois de dépenses, pour les imprévus.`;
    case "high_debt_ratio":
      return `Vos mensualités (${formatMoney(v.payments)}) représenteraient ${percent(v.ratio)} `
        + `de votre revenu. Au-delà de 40 %, la plupart des banques refusent le crédit.`;
    case "high_extra_cost":
      return `Les frais mensuels liés à l'achat (${formatMoney(v.extra_cost)}) représentent `
        + `${percent(v.ratio)} de votre revenu. Vérifiez ce montant : il comprend l'assurance, `
        + `l'entretien et l'usage, pas la mensualité du crédit.`;
    default:
      return "Une valeur saisie mérite d'être vérifiée.";
  }
}

// Avertissements affichés au-dessus du graphique, du plus grave au moins grave.
export function WarningList({ warnings }: { warnings: InputWarning[] }) {
  if (warnings.length === 0) return null;

  return (
    <ul aria-label="Points à vérifier" className="flex flex-col gap-2">
      {warnings.map((w) => (
        <li
          key={w.code}
          className={`rounded-md border-l-4 px-4 py-3 text-sm ${
            w.level === "danger"
              ? "border-grenade bg-grenade/5 text-grenade"
              : "border-safran bg-safran/10 text-encre"
          }`}
        >
          <span className="font-semibold">{w.level === "danger" ? "Risque élevé. " : "À vérifier. "}</span>
          {message(w)}
        </li>
      ))}
    </ul>
  );
}