"use client";

import { useState, type FormEvent } from "react";

import { ApiError, login, register } from "@/lib/api";

type Props = { onLoggedIn: () => void };

// Connexion ou création de compte, dans le même petit formulaire.
export function AuthForm({ onLoggedIn }: Props) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await (mode === "login" ? login(email, password) : register(email, password));
      onLoggedIn();
    } catch (e) {
      const status = e instanceof ApiError ? e.status : 0;
      setError(
        status === 401 ? "Email ou mot de passe incorrect."
        : status === 409 ? "Un compte existe déjà avec cet email. Connectez-vous."
        : status === 422 ? "Vérifiez l'email, et choisissez un mot de passe d'au moins 8 caractères."
        : "Connexion impossible : vérifiez que l'API tourne.",
      );
    } finally {
      setBusy(false);
    }
  };

  const field = "rounded-md border border-ligne px-3 py-2 outline-none focus:border-bleu focus:ring-2 focus:ring-bleu/20";

  return (
    <form onSubmit={submit} className="flex flex-col gap-3">
      <p className="text-sm text-pierre">
        {mode === "login"
          ? "Connectez-vous pour enregistrer vos simulations et les retrouver plus tard."
          : "Créez un compte gratuit pour enregistrer vos simulations."}
      </p>
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="flex flex-col gap-1.5">
          <span className="text-sm text-pierre">Email</span>
          <input type="email" autoComplete="email" required className={field}
                 value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label className="flex flex-col gap-1.5">
          <span className="text-sm text-pierre">Mot de passe</span>
          <input type="password" required minLength={8} className={field}
                 autoComplete={mode === "login" ? "current-password" : "new-password"}
                 value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
      </div>
      {error && <p role="alert" className="text-sm text-grenade">{error}</p>}
      <div className="flex flex-wrap items-center gap-4">
        <button type="submit" disabled={busy}
                className="rounded-md bg-bleu px-4 py-2 font-medium text-white hover:bg-bleu/90 disabled:opacity-60 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-bleu">
          {mode === "login" ? "Se connecter" : "Créer mon compte"}
        </button>
        <button type="button" className="text-sm text-bleu underline-offset-4 hover:underline"
                onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(null); }}>
          {mode === "login" ? "Pas encore de compte ? En créer un" : "Déjà un compte ? Se connecter"}
        </button>
      </div>
    </form>
  );
}