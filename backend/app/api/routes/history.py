"""Historique : enregistrer, lister et supprimer des simulations."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.simulations import to_decision, to_profile
from app.db.models import SavedSimulation
from app.db.session import get_db
from app.engine import health_score, project
from app.schemas.history import SavedOut, SaveRequest

router = APIRouter(prefix="/history", tags=["Historique"])


@router.post("", response_model=SavedOut, status_code=201)
def save_simulation(request: SaveRequest, db: Session = Depends(get_db)) -> SavedSimulation:
    """Enregistre une simulation. Les chiffres clés sont recalculés par le serveur."""
    profile = to_profile(request.profile)
    decision = to_decision(request.decision)
    result = project(profile, request.horizon_months, decision)

    saved = SavedSimulation(
        name=request.name,
        profile=request.profile.model_dump(),
        decision=request.decision.model_dump(),
        horizon_months=request.horizon_months,
        final_cash=result.final.cash,
        health_score=health_score(profile, decision).total,
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved


@router.get("", response_model=list[SavedOut])
def list_simulations(db: Session = Depends(get_db)) -> list[SavedSimulation]:
    """Les simulations enregistrées, de la plus récente à la plus ancienne."""
    query = select(SavedSimulation).order_by(SavedSimulation.id.desc())
    return list(db.scalars(query))


@router.delete("/{simulation_id}", status_code=204)
def delete_simulation(simulation_id: int, db: Session = Depends(get_db)) -> None:
    """Supprime une simulation enregistrée."""
    saved = db.get(SavedSimulation, simulation_id)
    if saved is None:
        raise HTTPException(status_code=404, detail="Simulation introuvable")
    db.delete(saved)
    db.commit()