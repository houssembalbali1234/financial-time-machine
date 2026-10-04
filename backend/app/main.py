"""Point d'entrée de l'API Financial Time Machine."""
from fastapi import FastAPI

from app.api.routes import simulations

app = FastAPI(
    title="Financial Time Machine API",
    description="Simulation, prédiction et recommandation financière personnalisée.",
    version="0.1.0",
)


@app.get("/health", tags=["Système"])
def health() -> dict:
    """Vérifie que l'API fonctionne."""
    return {"status": "ok", "version": app.version}


app.include_router(simulations.router)