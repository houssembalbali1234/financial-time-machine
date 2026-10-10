"""Connexion au modèle Llama servi par Ollama (gratuit, local, sans envoyer de données à l'extérieur)."""
from collections.abc import Callable

import httpx

LetterWriter = Callable[[str, str], str]   # (consigne, situation) -> texte
ChatModel = Callable[[list[dict]], str]     # (messages) -> réponse


def make_ollama_writer(base_url: str, model: str, timeout: float, temperature: float = 0.3,
                       client: httpx.Client | None = None) -> LetterWriter:
    """Fabrique une fonction qui envoie une consigne et une situation à Llama, et renvoie sa réponse."""
    chat = make_ollama_chat(base_url, model, timeout, temperature, client)

    def write(system: str, prompt: str) -> str:
        return chat([{"role": "system", "content": system}, {"role": "user", "content": prompt}])

    return write


def make_ollama_chat(base_url: str, model: str, timeout: float, temperature: float = 0.3,
                     client: httpx.Client | None = None) -> ChatModel:
    """Fabrique une fonction qui envoie une conversation à Llama et renvoie sa réponse."""
    http = client or httpx.Client(timeout=timeout)

    def chat(messages: list[dict]) -> str:
        response = http.post(f"{base_url}/api/chat", json={
            "model": model,
            "messages": messages,
            "stream": False,                     # on attend la réponse complète
            "options": {"temperature": temperature},   # bas = plus régulier, moins de dérapages
        })
        response.raise_for_status()
        return response.json()["message"]["content"].strip()

    return chat