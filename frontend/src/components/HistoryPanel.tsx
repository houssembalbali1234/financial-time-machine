"use client";

import { useEffect, useState } from "react";

import { AuthForm } from "@/components/AuthForm";
import {
  ApiError, clearToken, deleteSimulation, getMe, getToken, listHistory, saveSimulation,
  type Decision, type Profile, type SavedSimulation, type User,
} from "@/lib/api";
import { formatMoney } from "@/lib/format";

type Props = {
  profile: Profile;
  decision: Decision;
  horizon: number;
  onOpen: (saved: SavedSimulation) => void;
};

const dateFormat = new Intl.DateTimeFormat("fr-FR", { dateStyle: "medium", timeStyle: "short" });

type Session = { user: User | null; items: SavedSimulation[]; error: string | null };

// Retrouve l'utilisateur connecté (s'il y a un jeton) et son historique.
async function fetchSession(): Promise<Session> {
  if (!getToken()) return { user: null, items: [], error: null };
  try {
    const [user, items] = await Promise.all([getMe(), listHistory()]);
    return { user, items, error: null };
  } catch (e) {
    if (e instanceof ApiError && e.status === 401) clearToken();   // jeton expiré ou invalide
    return { user: null, items: [], error: e instanceof ApiError && e.status === 401
      ? null : "Impossible de charger l'historique." };
  }
}

// Enregistrer la simulation en cours et retrouver les précédentes (compte requis).
export function HistoryPanel({ profile, decision, horizon, onOpen }: Props) {
  const [user, setUser] = useState<User | null>(null);
  const [checking, setChecking] = useState(true);
  const [items, setItems] = useState<SavedSimulation[]>([]);
  const [name, setName] = useState("");
  const [status, setStatus] = useState<string | null>(null);

  const logout = () => {
    clearToken();
    setUser(null);
    setItems([]);
    setStatus(null);
  };

  // Un jeton expiré ou invalide (401) déconnecte proprement l'utilisateur.
  const handleError = (e: unknown, message: string) => {
    if (e instanceof ApiError && e.status === 401) logout();
    else setStatus(message);
  };

  const applySession = (session: Session) => {
    setUser(session.user);
    setItems(session.items);
    setStatus(session.error);
    setChecking(false);
  };

  // Au chargement de la page : l'utilisateur est-il déjà connecté ?
  useEffect(() => {
    let cancelled = false;
    fetchSession().then((session) => {
      if (!cancelled) applySession(session);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const save = async () => {
    const label = name.trim() || `${decision.name} à ${formatMoney(decision.price)}`;
    try {
      await saveSimulation(label, profile, decision, horizon);
      setName("");
      setStatus(`« ${label} » enregistrée.`);
      setItems(await listHistory());
    } catch (e) {
      handleError(e, "Enregistrement impossible : vérifiez que l'API et la base de données tournent.");
    }
  };

  const remove = async (item: SavedSimulation) => {
    try {
      await deleteSimulation(item.id);
      setStatus(`« ${item.name} » supprimée.`);
      setItems(await listHistory());
    } catch (e) {
      handleError(e, "Suppression impossible.");
    }
  };

  return (
    <section aria-labelledby="historique" className="flex flex-col gap-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 id="historique" className="font-display text-xl font-semibold">Mes simulations</h2>
        {user && (
          <p className="text-sm text-pierre">
            {user.email}{" "}
            <button type="button" onClick={logout} className="ml-2 text-bleu underline-offset-4 hover:underline">
              Se déconnecter
            </button>
          </p>
        )}
      </div>

      {checking ? null : !user ? (
        <AuthForm onLoggedIn={() => fetchSession().then(applySession)} />
      ) : (
        <>
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
        </>
      )}
    </section>
  );
}