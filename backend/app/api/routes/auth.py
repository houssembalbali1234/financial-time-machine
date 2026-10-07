"""Inscription, connexion et profil de l'utilisateur connecté."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.db.session import get_db
from app.schemas.auth import Credentials, TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["Comptes"])


@router.post("/register", response_model=TokenOut, status_code=201)
def register(credentials: Credentials, db: Session = Depends(get_db)) -> TokenOut:
    """Crée un compte et connecte directement l'utilisateur."""
    email = credentials.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Un compte existe déjà avec cet email")
    user = User(email=email, password_hash=hash_password(credentials.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenOut(access_token=create_access_token(user.id))


@router.post("/login", response_model=TokenOut)
def login(credentials: Credentials, db: Session = Depends(get_db)) -> TokenOut:
    """Vérifie l'email et le mot de passe, puis renvoie un jeton."""
    user = db.scalar(select(User).where(User.email == credentials.email.lower()))
    if user is None or not verify_password(credentials.password, user.password_hash):
        # Même message dans les deux cas : on ne révèle pas si l'email existe.
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Email ou mot de passe incorrect")
    return TokenOut(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    """Le compte actuellement connecté."""
    return user