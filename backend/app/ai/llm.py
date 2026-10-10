"""Connexion au modèle Llama servi par Ollama (gratuit, local, sans envoyer de données à l'extérieur)."""
from collections.abc import Callable

import httpx

LetterWriter = Callable[[str, str], str]   # (consigne, situation) -> texte


def make_ollama_writer(base_url: str, model: str, timeout: float,
                       client: httpx.Client | None = None) -> LetterWriter:
    """Fabrique une fonction qui envoie une consigne et une situation à Llama, et renvoie sa réponse."""
    http = client or httpx.Client(timeout=timeout)

    def write(system: str, prompt: str) -> str:
        response = http.post(f"{base_url}/api/chat", json={
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "stream": False,                     # on attend la réponse complète
            "options": {"temperature": 0.7},     # un peu de variété, sans délirer
        })
        response.raise_for_status()
        return response.json()["message"]["content"].strip()

    return write