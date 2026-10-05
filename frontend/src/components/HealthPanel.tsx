import type { HealthScoreResult } from "@/lib/api";
import { formatNumber } from "@/lib/format";

const gradeColor: Record<string, string> = {
  Excellente: "text-olive",
  Bonne: "text-olive",
  Fragile: "text-grenade",
  Critique: "text-grenade",
};

// La note de santé financière avant et après la décision, facteur par facteur.
export function HealthPanel({ health }: { health: HealthScoreResult }) {
  const after = health.after_decision ?? health.current;
  const impact = health.impact ?? 0;

  return (
    <section aria-labelledby="sante" className="flex flex-col gap-5">
      <h2 id="sante" className="font-display text-xl font-semibold">Santé financière</h2>

      <div className="flex items-end gap-6">
        <p className="chiffres flex items-baseline gap-2">
          <span className={`font-display text-6xl font-bold ${gradeColor[after.grade]}`}>
            {after.total}
          </span>
          <span className="text-pierre">/ 100, {after.grade.toLowerCase()}</span>
        </p>
        {health.after_decision && (
          <p className="chiffres pb-2 text-sm text-pierre">
            Aujourd&apos;hui : {health.current.total}.{" "}
            <span className={impact < 0 ? "text-grenade" : "text-olive"}>
              {impact > 0 ? "+" : ""}{impact} points
            </span>
          </p>
        )}
      </div>

      <ul className="flex flex-col gap-4">
        {after.factors.map((factor) => (
          <li key={factor.key} className="flex flex-col gap-1.5">
            <div className="flex justify-between text-sm">
              <span className="font-medium">{factor.label}</span>
              <span className="chiffres text-pierre">
                {formatNumber(factor.points, 1)} / {Math.round(factor.weight * 100)} points
              </span>
            </div>
            <div className="h-1.5 rounded-full bg-ligne" aria-hidden="true">
              <div
                className={`h-full rounded-full ${factor.score >= 60 ? "bg-olive" : "bg-grenade"}`}
                style={{ width: `${factor.score}%` }}
              />
            </div>
            <p className="text-sm text-pierre">{factor.explanation}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}