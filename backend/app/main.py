"""Point d'entrée de l'API Financial Time Machine."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, health_score, history, simulations
from app.db import models  # noqa: F401  (enregistre les tables auprès de Base)
from app.db.session import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Au démarrage : crée les tables qui n'existent pas encore.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Financial Time Machine API",
    description="Simulation, prédiction et recommandation financière personnalisée.",
    version="0.1.0",
    lifespan=lifespan,
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
app.include_router(history.router)
app.include_router(auth.router)