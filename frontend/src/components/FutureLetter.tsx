"use client";

import { useState } from "react";

import { writeFutureLetter, type Decision, type FutureLetter as Letter, type Profile } from "@/lib/api";

type Props = { profile: Profile; decision: Decision; horizon: number };

// « Une lettre de vous, dans quelques années », écrite par Llama à partir des chiffres du moteur.
export function FutureLetter({ profile, decision, horizon }: Props) {
  const [result, setResult] = useState<Letter | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const write = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      setResult(await writeFutureLetter(profile, decision, horizon));
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
          {loading ? "L'IA écrit votre lettre…" : result ? "Écrire une autre version" : "Lire ma lettre du futur"}
        </button>
        {loading && (
          <p role="status" className="mt-2 text-sm text-pierre">
            Cela peut prendre jusqu&apos;à 2 minutes sur un ordinateur sans carte graphique.
          </p>
        )}
      </div>

      {error && <p role="alert" className="text-sm text-grenade">{error}</p>}

      {result && (
        <article className="whitespace-pre-line rounded-md border-l-4 border-bleu bg-chaux px-5 py-4 leading-relaxed">
          {result.letter}
        </article>
      )}

      {result && result.verified && (
        <p className="text-sm text-olive">
          Chiffres vérifiés : chaque montant clé de la lettre correspond à votre simulation.
        </p>
      )}

      {result && !result.verified && (
        <div className="rounded-md border-l-4 border-safran bg-safran/10 px-4 py-3 text-sm">
          <p className="font-semibold">À lire avec prudence.</p>
          <p>L&apos;IA n&apos;a pas respecté toutes les consignes, malgré une seconde tentative :</p>
          <ul className="mt-1 list-disc pl-5">
            {result.problems.map((problem) => <li key={problem}>{problem}</li>)}
          </ul>
          <p className="mt-1">Les chiffres du graphique et des tableaux restent la référence.</p>
        </div>
      )}

      {result && (
        <p className="text-xs text-pierre">
          Texte généré par une IA à partir de vos chiffres. Ce n&apos;est pas un conseil financier.
        </p>
      )}
    </section>
  );
}