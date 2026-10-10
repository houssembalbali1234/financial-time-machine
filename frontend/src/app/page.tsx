"use client";

import { useEffect, useState } from "react";

import { Assistant } from "@/components/Assistant";
import { FutureChart } from "@/components/FutureChart";
import { FutureLetter } from "@/components/FutureLetter";
import { HealthPanel } from "@/components/HealthPanel";
import { HistoryPanel } from "@/components/HistoryPanel";
import { NumberField } from "@/components/NumberField";
import { ScenarioTable } from "@/components/ScenarioTable";
import { StressTest } from "@/components/StressTest";
import { WarningList } from "@/components/WarningList";
import {
  compareScenarios, getHealthScore, simulate,
  type Decision, type HealthScoreResult, type Profile, type SavedSimulation,
  type ScenariosResult, type SimulationResult,
} from "@/lib/api";
import { formatMoney } from "@/lib/format";
import { HORIZONS, PRESETS, type Horizon } from "@/lib/presets";

type Results = {
  withDecision: SimulationResult;
  withoutDecision: SimulationResult;
  health: HealthScoreResult;
  scenarios: ScenariosResult;
};

const DEFAULT_PROFILE: Profile = {
  monthly_income: 2500,
  monthly_expenses: 1700,
  cash: 12000,
  annual_inflation: 0.03,
};

// Bouton d'un groupe de choix (type de décision, durée d'observation)
function choiceClass(selected: boolean): string {
  return `rounded-full border px-3 py-1.5 text-sm transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-bleu ${
    selected ? "border-bleu bg-bleu text-white" : "border-ligne bg-papier text-encre hover:border-bleu"
  }`;
}

export default function Home() {
  const [profile, setProfile] = useState(DEFAULT_PROFILE);
  const [presetKey, setPresetKey] = useState(PRESETS[0].key);
  const [decision, setDecision] = useState<Decision>(PRESETS[0].decision);
  const [horizon, setHorizon] = useState<Horizon>(PRESETS[0].horizon);
  const [results, setResults] = useState<Results | null>(null);
  const [error, setError] = useState<string | null>(null);

  // What-If : on recalcule 300 ms après la dernière modification d'un champ.
  useEffect(() => {
    const timer = setTimeout(async () => {
      try {
        const [withDecision, withoutDecision, health, scenarios] = await Promise.all([
          simulate(profile, decision, horizon),
          simulate(profile, null, horizon),
          getHealthScore(profile, decision),
          compareScenarios(profile, decision, horizon),
        ]);
        setResults({ withDecision, withoutDecision, health, scenarios });
        setError(null);
      } catch {
        setError("Impossible de calculer : vérifiez que l'API tourne sur le port 8000 "
          + "et que tous les champs sont remplis avec des valeurs valides.");
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [profile, decision, horizon]);

  const choosePreset = (key: string) => {
    const preset = PRESETS.find((p) => p.key === key);
    if (!preset) return;
    setPresetKey(key);
    setDecision(preset.decision);
    setHorizon(preset.horizon);
  };

  // Recharge une simulation enregistrée dans le formulaire.
  const openSaved = (saved: SavedSimulation) => {
    const p = saved.profile;
    const d = saved.decision;
    setProfile({
      monthly_income: p.monthly_income,
      monthly_expenses: p.monthly_expenses,
      cash: p.cash,
      annual_inflation: p.annual_inflation,
    });
    setDecision({
      name: d.name,
      price: d.price,
      down_payment: d.down_payment,
      loan_annual_rate: d.loan_annual_rate,
      loan_months: d.loan_months,
      asset_annual_depreciation: d.asset_annual_depreciation,
      extra_monthly_cost: d.extra_monthly_cost,
    });
    const known = HORIZONS.find((h) => h.value === saved.horizon_months);
    setHorizon(known ? known.value : 36);
    setPresetKey(PRESETS.find((preset) => preset.label === d.name)?.key ?? "");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const updateProfile = (key: keyof Profile) => (value: number) =>
    setProfile((p) => ({ ...p, [key]: value }));
  const updateDecision = (key: keyof Decision) => (value: number) =>
    setDecision((d) => ({ ...d, [key]: value }));

  const horizonLabel = HORIZONS.find((h) => h.value === horizon)?.label ?? `${horizon} mois`;
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

            <div role="radiogroup" aria-label="Type de décision" className="flex flex-wrap gap-2">
              {PRESETS.map((preset) => (
                <button key={preset.key} type="button" role="radio"
                        aria-checked={preset.key === presetKey}
                        className={choiceClass(preset.key === presetKey)}
                        onClick={() => choosePreset(preset.key)}>
                  {preset.label}
                </button>
              ))}
            </div>

            <label className="flex flex-col gap-1.5">
              <span className="text-sm text-pierre">Nom du projet</span>
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
            <NumberField label="Évolution de la valeur par an" suffix="%" step={1} min={-100}
                         value={Math.round(-decision.asset_annual_depreciation * 1000) / 10}
                         onChange={(v) => updateDecision("asset_annual_depreciation")(-v / 100)} />
            <p className="-mt-2 text-xs text-pierre">
              Négatif si le bien perd de la valeur (voiture : -12 %), -100 % s&apos;il n&apos;en garde
              aucune (études, mariage).
            </p>
          </fieldset>
        </aside>

        <main className="order-1 flex flex-col gap-10 lg:order-2">
          <section className="flex flex-col gap-4">
            <h1 className="font-display text-3xl font-bold leading-tight sm:text-4xl">
              {decision.name || "Ce projet"} à {formatMoney(decision.price || 0)}&nbsp;: et si je
              me lançais maintenant&nbsp;?
            </h1>

            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="max-w-prose text-pierre">
                Votre épargne mois par mois pendant {horizonLabel}, avec et sans ce projet.
              </p>
              <div role="radiogroup" aria-label="Durée observée" className="flex gap-2">
                {HORIZONS.map((h) => (
                  <button key={h.value} type="button" role="radio"
                          aria-checked={h.value === horizon}
                          className={choiceClass(h.value === horizon)}
                          onClick={() => setHorizon(h.value)}>
                    {h.label}
                  </button>
                ))}
              </div>
            </div>

            {error && (
              <p role="alert" className="rounded-md border border-grenade/30 bg-grenade/5 p-4 text-grenade">
                {error}
              </p>
            )}

            {results && (
              <>
                <WarningList warnings={results.withDecision.warnings} />
                <FutureChart
                  withDecision={results.withDecision.months}
                  withoutDecision={results.withoutDecision.months}
                  decisionName={decision.name || "le projet"}
                  turningMonth={turningMonth}
                />
                <dl className="chiffres grid grid-cols-2 gap-6 border-t border-ligne pt-6 sm:grid-cols-3">
                  <div>
                    <dt className="text-sm text-pierre">Épargne dans {horizonLabel}</dt>
                    <dd className="font-display text-2xl font-semibold">
                      {formatMoney(results.withDecision.summary.final_cash)}
                    </dd>
                    <dd className="text-sm text-pierre">
                      {formatMoney(results.withoutDecision.summary.final_cash)} sans ce projet
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

          {results && (
            <div className="rounded-lg border border-ligne bg-papier p-6">
              <ScenarioTable result={results.scenarios} />
            </div>
          )}

          <div className="rounded-lg border border-ligne bg-papier p-6">
            <StressTest profile={profile} decision={decision} horizon={horizon} />
          </div>

          <div className="rounded-lg border border-ligne bg-papier p-6">
            <Assistant profile={profile} decision={decision} horizon={horizon} />
          </div>

          <div className="rounded-lg border border-ligne bg-papier p-6">
            <FutureLetter profile={profile} decision={decision} horizon={horizon} />
          </div>

          <div className="rounded-lg border border-ligne bg-papier p-6">
            <HistoryPanel profile={profile} decision={decision} horizon={horizon} onOpen={openSaved} />
          </div>
        </main>
      </div>
    </div>
  );
}