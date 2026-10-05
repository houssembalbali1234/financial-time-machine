"use client";

import { useEffect, useState } from "react";

import {
  deleteSimulation, listHistory, saveSimulation,
  type Decision, type Profile, type SavedSimulation,
} from "@/lib/api";
import { formatMoney } from "@/lib/format";

type Props = {
  profile: Profile;
  decision: Decision;
  horizon: number;
  onOpen: (saved: SavedSimulation) => void;
};

const dateFormat = new Intl.DateTimeFormat("fr-FR", { dateStyle: "medium", timeStyle: "short" });

// Enregistrer la simulation en cours et retrouver les précédentes.
export function HistoryPanel({ profile, decision, horizon, onOpen }: Props) {
  const [items, setItems] = useState<SavedSimulation[]>([]);
  const [name, setName] = useState("");
  const [status, setStatus] = useState<string | null>(null);

  const refresh = () =>
    listHistory().then(setItems).catch(() => setStatus("Impossible de charger l'historique."));

  useEffect(() => {
    refresh();
  }, []);

  const save = async () => {
    const label = name.trim() || `${decision.name} à ${formatMoney(decision.price)}`;
    try {
      await saveSimulation(label, profile, decision, horizon);
      setName("");
      setStatus(`« ${label} » enregistrée.`);
      refresh();
    } catch {
      setStatus("Enregistrement impossible : vérifiez que l'API et la base de données tournent.");
    }
  };

  const remove = async (item: SavedSimulation) => {
    try {
      await deleteSimulation(item.id);
      setStatus(`« ${item.name} » supprimée.`);
      refresh();
    } catch {
      setStatus("Suppression impossible.");
    }
  };

  return (
    <section aria-labelledby="historique" className="flex flex-col gap-4">
      <h2 id="historique" className="font-display text-xl font-semibold">Mes simulations</h2>

      <div className="flex flex-wrap gap-2">
        <input
          aria-label="Nom de la simulation"
          placeholder={`${decision.name} à ${formatMoney(decision.price || 0)}`}
          className="min-w-0 flex-1 rounded-md border border-ligne px-3 py-2 outline-none focus:border-bleu focus:ring-2 focus:ring-bleu/20"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <button type="button" onClick={save}
                className="rounded-md bg-bleu px-4 py-2 font-medium text-white hover:bg-bleu/90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-bleu">
          Enregistrer cette simulation
        </button>
      </div>

      {status && <p role="status" className="text-sm text-pierre">{status}</p>}

      {items.length === 0 ? (
        <p className="text-sm text-pierre">
          Aucune simulation enregistrée. Enregistrez celle-ci pour pouvoir la comparer plus tard.
        </p>
      ) : (
        <ul className="flex flex-col divide-y divide-ligne">
          {items.map((item) => (
            <li key={item.id} className="chiffres flex flex-wrap items-center justify-between gap-3 py-3">
              <div>
                <p className="font-medium">{item.name}</p>
                <p className="text-sm text-pierre">
                  Enregistrée le {dateFormat.format(new Date(item.created_at))}. Santé{" "}
                  {item.health_score}/100, épargne finale {formatMoney(item.final_cash)}.
                </p>
              </div>
              <div className="flex gap-2">
                <button type="button" onClick={() => onOpen(item)}
                        className="rounded-md border border-ligne px-3 py-1.5 text-sm hover:border-bleu">
                  Ouvrir
                </button>
                <button type="button" onClick={() => remove(item)}
                        className="rounded-md border border-ligne px-3 py-1.5 text-sm text-grenade hover:border-grenade">
                  Supprimer
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}