"use client";

import { useState } from "react";

import { writeFutureLetter, type Decision, type Profile } from "@/lib/api";

type Props = { profile: Profile; decision: Decision; horizon: number };

// « Une lettre de vous, dans quelques années », écrite par Llama à partir des chiffres du moteur.
export function FutureLetter({ profile, decision, horizon }: Props) {
  const [letter, setLetter] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const write = async () => {
    setLoading(true);
    setError(null);
    setLetter(null);
    try {
      const result = await writeFutureLetter(profile, decision, horizon);
      setLetter(result.letter);
    } catch {
      setError("Llama ne répond pas. Vérifiez que le conteneur Ollama tourne, puis réessayez.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section aria-labelledby="lettre" className="flex flex-col gap-4">
      <h2 id="lettre" className="font-display text-xl font-semibold">Une lettre de votre futur</h2>
      <p className="text-sm text-pierre">
        L&apos;IA écrit ce que vous pourriez vous dire dans {Math.round(horizon / 12)} ans, à partir
        des chiffres de cette simulation. Elle tourne sur votre propre serveur : vos données ne
        sortent pas.
      </p>

      <div>
        <button type="button" onClick={write} disabled={loading}
                className="rounded-md bg-bleu px-4 py-2 font-medium text-white hover:bg-bleu/90 disabled:opacity-60 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-bleu">
          {loading ? "L'IA écrit votre lettre…" : letter ? "Écrire une autre version" : "Lire ma lettre du futur"}
        </button>
        {loading && (
          <p role="status" className="mt-2 text-sm text-pierre">
            Cela peut prendre jusqu&apos;à 2 minutes sur un ordinateur sans carte graphique.
          </p>
        )}
      </div>

      {error && <p role="alert" className="text-sm text-grenade">{error}</p>}

      {letter && (
        <article className="whitespace-pre-line rounded-md border-l-4 border-bleu bg-chaux px-5 py-4 leading-relaxed">
          {letter}
        </article>
      )}

      {letter && (
        <p className="text-xs text-pierre">
          Texte généré par une IA à partir de vos chiffres. Ce n&apos;est pas un conseil financier.
        </p>
      )}
    </section>
  );
}