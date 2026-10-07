"""Dépendances partagées par les routes."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import read_access_token
from app.db.models import User
from app.db.session import get_db

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    """Retrouve l'utilisateur à partir du jeton envoyé dans l'en-tête Authorization."""
    user_id = read_access_token(credentials.credentials) if credentials else None
    user = db.get(User, user_id) if user_id else None
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Connexion requise",
                            headers={"WWW-Authenticate": "Bearer"})
    return user