"""Fonctions d'intelligence artificielle (Llama via Ollama)."""
from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException

from app.ai import assistant
from app.ai.letter import SYSTEM_PROMPT, build_facts, build_prompt, check_letter
from app.ai.llm import ChatModel, LetterWriter, make_ollama_chat, make_ollama_writer
from app.api.routes.simulations import to_decision, to_profile
from app.core.config import settings
from app.schemas.ai import AskRequest, AskResponse, LetterRequest, LetterResponse

router = APIRouter(prefix="/ai", tags=["Intelligence artificielle"])

MAX_ATTEMPTS = 2   # une première version, puis une correction si besoin


def get_letter_writer() -> LetterWriter:
    """Le modèle utilisé pour écrire. Remplacé par une fausse version dans les tests."""
    return make_ollama_writer(settings.ollama_url, settings.ollama_model,
                              settings.ollama_timeout_seconds)


def get_chat_model() -> ChatModel:
    """Le modèle utilisé par l'assistant. Remplacé par une fausse version dans les tests."""
    return make_ollama_chat(settings.ollama_url, settings.ollama_model,
                            settings.ollama_timeout_seconds)


def llama_unavailable(error: Exception) -> HTTPException:
    return HTTPException(
        status_code=502,
        detail=f"Llama ne répond pas. Vérifiez qu'Ollama tourne et que le modèle "
               f"{settings.ollama_model} est téléchargé.",
    )


@router.post("/future-letter", response_model=LetterResponse)
def future_letter(request: LetterRequest,
                  write: LetterWriter = Depends(get_letter_writer)) -> LetterResponse:
    """Une lettre de « vous dans N ans », écrite par Llama puis vérifiée par le code."""
    facts = build_facts(to_profile(request.profile), to_decision(request.decision),
                        request.horizon_months)
    letter, problems = "", []
    try:
        for _ in range(MAX_ATTEMPTS):
            letter = write(SYSTEM_PROMPT, build_prompt(facts, problems))
            problems = check_letter(letter, facts)
            if not problems:
                break
    except Exception as error:   # Ollama éteint, modèle non téléchargé, délai dépassé...
        raise llama_unavailable(error) from error
    return LetterResponse(letter=letter, verified=not problems, problems=problems,
                          facts=asdict(facts))


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest, chat: ChatModel = Depends(get_chat_model)) -> AskResponse:
    """L'assistant répond à une question sur la simulation, avec les seuls chiffres du moteur."""
    context, allowed = assistant.build_context(to_profile(request.profile),
                                               to_decision(request.decision), request.horizon_months)
    messages = assistant.build_messages(context, request.question,
                                        [m.model_dump() for m in request.history])
    try:
        answer = chat(messages)
        invented = assistant.invented_numbers(answer, allowed)
        if invented:   # un montant inventé : on redemande une fois, en le signalant
            messages += [
                {"role": "assistant", "content": answer},
                {"role": "user", "content": "Ta réponse contient des montants absents de la situation ("
                 + ", ".join(f"{n:.0f}" for n in invented)
                 + "). Réponds à nouveau en n'utilisant que les chiffres fournis."},
            ]
            answer = chat(messages)
            invented = assistant.invented_numbers(answer, allowed)
    except Exception as error:
        raise llama_unavailable(error) from error
    return AskResponse(answer=answer, verified=not invented)