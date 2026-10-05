"use client";

import { useEffect, useState } from "react";

import { stressTest, type Decision, type Profile, type Shock, type StressResult } from "@/lib/api";
import { formatMoney } from "@/lib/format";

const SHOCKS: { key: string; label: string; shock: Shock }[] = [
  { key: "job3", label: "Perte d'emploi 3 mois",
    shock: { name: "perte_emploi_3", income_factor: 0, start_month: 1, duration_months: 3 } },
  { key: "job6", label: "Perte d'emploi 6 mois",
    shock: { name: "perte_emploi_6", income_factor: 0, start_month: 1, duration_months: 6 } },
  { key: "cut30", label: "Revenu -30 % pendant 1 an",
    shock: { name: "baisse_30", income_factor: 0.7, start_month: 1, duration_months: 12 } },
];

type Props = { profile: Profile; decision: Decision; horizon: number };

// « Et si un coup dur arrivait juste après le projet ? »
export function StressTest({ profile, decision, horizon }: Props) {
  const [choice, setChoice] = useState(SHOCKS[0].key);
  const [result, setResult] = useState<StressResult | null>(null);

  useEffect(() => {
    const shock = SHOCKS.find((s) => s.key === choice)!.shock;
    const timer = setTimeout(() => {
      stressTest(profile, decision, shock, horizon).then(setResult).catch(() => setResult(null));
    }, 300);
    return () => clearTimeout(timer);
  }, [profile, decision, horizon, choice]);

  const stressed = result?.stressed;

  return (
    <section aria-labelledby="stress" className="flex flex-col gap-4">
      <h2 id="stress" className="font-display text-xl font-semibold">Et si un coup dur arrivait&nbsp;?</h2>

      <div role="radiogroup" aria-label="Type de coup dur" className="flex flex-wrap gap-2">
        {SHOCKS.map((s) => (
          <button key={s.key} type="button" role="radio" aria-checked={s.key === choice}
                  onClick={() => setChoice(s.key)}
                  className={`rounded-full border px-3 py-1.5 text-sm focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-bleu ${
                    s.key === choice ? "border-bleu bg-bleu text-white" : "border-ligne bg-papier hover:border-bleu"
                  }`}>
            {s.label}
          </button>
        ))}
      </div>

      {result && stressed && (
        <div className="chiffres flex flex-col gap-3">
          <p className="text-lg">
            {stressed.months_negative === 0
              ? "Votre épargne absorbe ce choc sans passer dans le rouge."
              : `Votre épargne passerait dans le rouge au mois ${stressed.first_negative_month}, `
                + `et y resterait ${stressed.months_negative} mois.`}
          </p>
          <dl className="grid grid-cols-2 gap-6 sm:grid-cols-3">
            <div>
              <dt className="text-sm text-pierre">Argent perdu</dt>
              <dd className="font-display text-2xl font-semibold">{formatMoney(result.cash_lost)}</dd>
            </div>
            <div>
              <dt className="text-sm text-pierre">Épargne au plus bas</dt>
              <dd className={`font-display text-2xl font-semibold ${stressed.min_cash < 0 ? "text-grenade" : ""}`}>
                {formatMoney(stressed.min_cash)}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-pierre">Sans aucun revenu, vous tiendriez</dt>
              <dd className="font-display text-2xl font-semibold">
                {result.months_of_resilience} mois
              </dd>
            </div>
          </dl>
        </div>
      )}
    </section>
  );
}