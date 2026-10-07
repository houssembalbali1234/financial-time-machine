"""Mots de passe et jetons de connexion."""
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

ALGORITHM = "HS256"
password_hash = PasswordHash.recommended()   # Argon2, l'algorithme recommandé aujourd'hui


def hash_password(password: str) -> str:
    """Transforme un mot de passe en empreinte : on ne stocke jamais le mot de passe lui-même."""
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_access_token(user_id: int) -> str:
    """Jeton signé qui prouve l'identité de l'utilisateur pendant 24 heures."""
    expires = datetime.now(UTC) + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode({"sub": str(user_id), "exp": expires}, settings.secret_key, algorithm=ALGORITHM)


def read_access_token(token: str) -> int | None:
    """Renvoie l'identifiant de l'utilisateur, ou None si le jeton est invalide ou expiré."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        return None