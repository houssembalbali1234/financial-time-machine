"use client";

import { useState, type FormEvent } from "react";

import { askAssistant, type ChatMessage, type Decision, type Profile } from "@/lib/api";

type Props = { profile: Profile; decision: Decision; horizon: number };

type Message = ChatMessage & { verified?: boolean };

const SUGGESTIONS = [
  "Et si j'attendais un an ?",
  "Combien je paierai par mois ?",
  "Que se passe-t-il si je perds mon emploi ?",
];

// Questions-réponses avec Llama, à partir des seuls chiffres de la simulation en cours.
export function Assistant({ profile, decision, horizon }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const ask = async (text: string) => {
    const q = text.trim();
    if (q.length < 2 || loading) return;
    const history = messages.map(({ role, content }) => ({ role, content }));
    setMessages((m) => [...m, { role: "user", content: q }]);
    setQuestion("");
    setLoading(true);
    setError(null);
    try {
      const result = await askAssistant(profile, decision, horizon, q, history);
      setMessages((m) => [...m, { role: "assistant", content: result.answer, verified: result.verified }]);
    } catch {
      setError("Llama ne répond pas. Vérifiez que le conteneur Ollama tourne, puis réessayez.");
    } finally {
      setLoading(false);
    }
  };

  const submit = (event: FormEvent) => {
    event.preventDefault();
    ask(question);
  };

  return (
    <section aria-labelledby="assistant" className="flex flex-col gap-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 id="assistant" className="font-display text-xl font-semibold">Posez vos questions</h2>
        {messages.length > 0 && (
          <button type="button" onClick={() => setMessages([])}
                  className="text-sm text-bleu underline-offset-4 hover:underline">
            Nouvelle conversation
          </button>
        )}
      </div>
      <p className="text-sm text-pierre">
        L&apos;assistant répond à partir des chiffres de cette simulation. Si vous modifiez le
        formulaire, ses prochaines réponses en tiennent compte.
      </p>

      {messages.length > 0 && (
        <ol aria-live="polite" className="flex flex-col gap-3">
          {messages.map((m, i) => (
            <li key={i} className={m.role === "user" ? "self-end max-w-[85%]" : "max-w-[85%]"}>
              <p className={`whitespace-pre-line rounded-lg px-4 py-2.5 ${
                m.role === "user" ? "bg-bleu text-white" : "bg-chaux"}`}>
                {m.content}
              </p>
              {m.role === "assistant" && m.verified === false && (
                <p className="mt-1 text-xs text-encre">
                  Cette réponse contient un montant absent de votre simulation : fiez-vous au graphique.
                </p>
              )}
            </li>
          ))}
        </ol>
      )}

      {loading && <p role="status" className="text-sm text-pierre">L&apos;assistant réfléchit… (jusqu&apos;à 2 minutes)</p>}
      {error && <p role="alert" className="text-sm text-grenade">{error}</p>}

      {messages.length === 0 && (
        <div className="flex flex-wrap gap-2">
          {SUGGESTIONS.map((s) => (
            <button key={s} type="button" onClick={() => ask(s)} disabled={loading}
                    className="rounded-full border border-ligne bg-papier px-3 py-1.5 text-sm hover:border-bleu disabled:opacity-60">
              {s}
            </button>
          ))}
        </div>
      )}

      <form onSubmit={submit} className="flex gap-2">
        <input
          aria-label="Votre question"
          placeholder="Votre question sur cette simulation"
          maxLength={500}
          className="min-w-0 flex-1 rounded-md border border-ligne px-3 py-2 outline-none focus:border-bleu focus:ring-2 focus:ring-bleu/20"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button type="submit" disabled={loading || question.trim().length < 2}
                className="rounded-md bg-bleu px-4 py-2 font-medium text-white hover:bg-bleu/90 disabled:opacity-60 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-bleu">
          Envoyer
        </button>
      </form>
    </section>
  );
}