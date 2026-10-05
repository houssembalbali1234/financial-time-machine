"use client";

import { useEffect, useState } from "react";

import { FutureChart } from "@/components/FutureChart";
import { HealthPanel } from "@/components/HealthPanel";
import { NumberField } from "@/components/NumberField" ;
import {
  getHealthScore, simulate,
  type Decision, type HealthScoreResult, type Profile, type SimulationResult,
} from "@/lib/api";
import { formatMoney } from "@/lib/format";

type Results = {
  withDecision: SimulationResult;
  withoutDecision: SimulationResult;
  health: HealthScoreResult;
};

const DEFAULT_PROFILE: Profile = {
  monthly_income: 2500,
  monthly_expenses: 1700,
  cash: 12000,
  annual_inflation: 0.03,
};

const DEFAULT_DECISION: Decision = {
  name: "Voiture",
  price: 30000,
  down_payment: 6000,
  loan_annual_rate: 0.065,
  loan_months: 60,
  asset_annual_depreciation: 0.12,
  extra_monthly_cost: 200,
};

export default function Home() {
  const [profile, setProfile] = useState(DEFAULT_PROFILE);
  const [decision, setDecision] = useState(DEFAULT_DECISION);
  const [results, setResults] = useState<Results | null>(null);
  const [error, setError] = useState<string | null>(null);

  // What-If : on recalcule 300 ms après la dernière modification d'un champ.
  useEffect(() => {
    const timer = setTimeout(async () => {
      try {
        const [withDecision, withoutDecision, health] = await Promise.all([
          simulate(profile, decision),
          simulate(profile, null),
          getHealthScore(profile, decision),
        ]);
        setResults({ withDecision, withoutDecision, health });
        setError(null);
      } catch {
        setError("Impossible de calculer : vérifiez que l'API tourne sur le port 8000 "
          + "et que tous les champs sont remplis avec des valeurs valides.");
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [profile, decision]);

  const updateProfile = (key: keyof Profile) => (value: number) =>
    setProfile((p) => ({ ...p, [key]: value }));
  const updateDecision = (key: keyof Decision) => (value: number) =>
    setDecision((d) => ({ ...d, [key]: value }));

  const turningMonth = results?.withDecision.months.find((m) => m.cash_flow < 0)?.month ?? null;

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-10 px-5 py-8 lg:py-12">
      <header className="flex items-baseline justify-between gap-4">
        <p className="font-display text-lg font-bold text-bleu">Financial Time Machine</p>
        <p className="hidden text-sm text-pierre sm:block">Simulation à titre éducatif, pas un conseil financier.</p>
      </header>

      <div className="grid gap-10 lg:grid-cols-[20rem_1fr]">
        <aside className="order-2 flex flex-col gap-8 rounded-lg border border-ligne bg-papier p-6 lg:order-1 lg:self-start">
          <fieldset className="flex flex-col gap-4">
            <legend className="mb-2 font-display text-lg font-semibold">Votre situation</legend>
            <NumberField label="Revenu mensuel net" suffix="€" value={profile.monthly_income}
                         onChange={updateProfile("monthly_income")} />
            <NumberField label="Dépenses mensuelles" suffix="€" value={profile.monthly_expenses}
                         onChange={updateProfile("monthly_expenses")} />
            <NumberField label="Épargne disponible" suffix="€" value={profile.cash}
                         step={1000} onChange={updateProfile("cash")} />
            <NumberField label="Inflation annuelle" suffix="%" step={0.5}
                         value={Math.round(profile.annual_inflation * 1000) / 10}
                         onChange={(v) => updateProfile("annual_inflation")(v / 100)} />
          </fieldset>

          <fieldset className="flex flex-col gap-4">
            <legend className="mb-2 font-display text-lg font-semibold">Votre décision</legend>
            <label className="flex flex-col gap-1.5">
              <span className="text-sm text-pierre">Ce que vous voulez acheter</span>
              <input
                className="rounded-md border border-ligne px-3 py-2 outline-none focus:border-bleu focus:ring-2 focus:ring-bleu/20"
                value={decision.name}
                onChange={(e) => setDecision((d) => ({ ...d, name: e.target.value }))}
              />
            </label>
            <NumberField label="Prix" suffix="€" step={1000} value={decision.price}
                         onChange={updateDecision("price")} />
            <NumberField label="Apport" suffix="€" step={1000} value={decision.down_payment}
                         onChange={updateDecision("down_payment")} />
            <NumberField label="Taux du crédit" suffix="%" step={0.25}
                         value={Math.round(decision.loan_annual_rate * 10000) / 100}
                         onChange={(v) => updateDecision("loan_annual_rate")(v / 100)} />
            <NumberField label="Durée du crédit" suffix="mois" step={12} value={decision.loan_months}
                         onChange={updateDecision("loan_months")} />
            <NumberField label="Frais mensuels liés à l'achat" suffix="€" step={50}
                         value={decision.extra_monthly_cost}
                         onChange={updateDecision("extra_monthly_cost")} />
          </fieldset>
        </aside>

        <main className="order-1 flex flex-col gap-10 lg:order-2">
          <section className="flex flex-col gap-4">
            <h1 className="font-display text-3xl font-bold leading-tight sm:text-4xl">
              {decision.name || "Cet achat"} à {formatMoney(decision.price || 0)}&nbsp;: et si je
              l&apos;achetais maintenant&nbsp;?
            </h1>
            <p className="max-w-prose text-pierre">
              Votre épargne mois par mois pendant 3 ans, avec et sans cet achat.
            </p>

            {error && (
              <p role="alert" className="rounded-md border border-grenade/30 bg-grenade/5 p-4 text-grenade">
                {error}
              </p>
            )}

            {results && (
              <>
                <FutureChart
                  withDecision={results.withDecision.months}
                  withoutDecision={results.withoutDecision.months}
                  decisionName={decision.name || "l'achat"}
                  turningMonth={turningMonth}
                />
                <dl className="chiffres grid grid-cols-2 gap-6 border-t border-ligne pt-6 sm:grid-cols-3">
                  <div>
                    <dt className="text-sm text-pierre">Épargne dans 3 ans</dt>
                    <dd className="font-display text-2xl font-semibold">
                      {formatMoney(results.withDecision.summary.final_cash)}
                    </dd>
                    <dd className="text-sm text-pierre">
                      {formatMoney(results.withoutDecision.summary.final_cash)} sans l&apos;achat
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm text-pierre">Crédit restant à payer</dt>
                    <dd className="font-display text-2xl font-semibold">
                      {formatMoney(results.withDecision.summary.final_debt)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm text-pierre">Épargne au plus bas</dt>
                    <dd className={`font-display text-2xl font-semibold ${
                      results.withDecision.summary.min_cash < 0 ? "text-grenade" : ""}`}>
                      {formatMoney(results.withDecision.summary.min_cash)}
                    </dd>
                  </div>
                </dl>
              </>
            )}
          </section>

          {results && (
            <div className="rounded-lg border border-ligne bg-papier p-6">
              <HealthPanel health={results.health} />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}