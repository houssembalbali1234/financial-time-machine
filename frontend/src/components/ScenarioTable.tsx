import type { ScenariosResult } from "@/lib/api";
import { formatMoney } from "@/lib/format";

const LABELS: Record<string, string> = {
  maintenant: "Maintenant",
  moins_cher: "Moins cher",
  dans_6_mois: "Dans 6 mois",
  dans_12_mois: "Dans 12 mois",
};

const ORDER = ["maintenant", "moins_cher", "dans_6_mois", "dans_12_mois"];

// Quatre façons de réaliser le même projet, comparées côte à côte.
export function ScenarioTable({ result }: { result: ScenariosResult }) {
  const rows = [...result.scenarios].sort((a, b) => ORDER.indexOf(a.key) - ORDER.indexOf(b.key));

  return (
    <section aria-labelledby="scenarios" className="flex flex-col gap-4">
      <h2 id="scenarios" className="font-display text-xl font-semibold">Quand et comment le faire</h2>
      <div className="overflow-x-auto">
        <table className="chiffres w-full text-left text-sm">
          <thead className="text-pierre">
            <tr className="border-b border-ligne">
              <th scope="col" className="py-2 pr-4 font-normal">Option</th>
              <th scope="col" className="py-2 pr-4 font-normal">Prix</th>
              <th scope="col" className="py-2 pr-4 font-normal">Épargne au plus bas</th>
              <th scope="col" className="py-2 font-normal">Épargne à la fin</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((s) => {
              const recommended = s.key === result.recommended;
              return (
                <tr key={s.key} className={`border-b border-ligne ${recommended ? "bg-bleu/5" : ""}`}>
                  <th scope="row" className="py-3 pr-4 font-medium">
                    {LABELS[s.key] ?? s.key}
                    {recommended && (
                      <span className="ml-2 rounded-full bg-bleu px-2 py-0.5 text-xs font-normal text-white">
                        Recommandé
                      </span>
                    )}
                  </th>
                  <td className="py-3 pr-4">{formatMoney(s.price)}</td>
                  <td className={`py-3 pr-4 ${s.summary.min_cash < 0 ? "text-grenade" : ""}`}>
                    {formatMoney(s.summary.min_cash)}
                  </td>
                  <td className="py-3">{formatMoney(s.summary.final_cash)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="text-sm text-pierre">
        L&apos;option recommandée est la première qui garde toujours au moins 3 mois de sorties en
        épargne, avec des crédits sous 40 % du revenu.
      </p>
    </section>
  );
}