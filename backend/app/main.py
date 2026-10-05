"""Point d'entrée de l'API Financial Time Machine."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health_score, simulations

app = FastAPI(
    title="Financial Time Machine API",
    description="Simulation, prédiction et recommandation financière personnalisée.",
    version="0.1.0",
)

# Autorise le frontend (Next.js) à appeler l'API depuis le navigateur
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Système"])
def health() -> dict:
    """Vérifie que l'API fonctionne."""
    return {"status": "ok", "version": app.version}


app.include_router(simulations.router)
app.include_router(health_score.router)