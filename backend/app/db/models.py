"""Tables de la base de données."""
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class SavedSimulation(Base):
    """Une simulation enregistrée par l'utilisateur, pour la retrouver plus tard."""
    __tablename__ = "simulations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    profile: Mapped[dict] = mapped_column(JSON)
    decision: Mapped[dict] = mapped_column(JSON)
    horizon_months: Mapped[int] = mapped_column(Integer)
    final_cash: Mapped[float] = mapped_column(Float)
    health_score: Mapped[int] = mapped_column(Integer)