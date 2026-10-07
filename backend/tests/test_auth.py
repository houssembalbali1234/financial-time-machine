"""Tests des comptes utilisateurs."""
import uuid

from fastapi.testclient import TestClient

from app.core.security import hash_password, verify_password
from app.main import app

client = TestClient(app)


def unique_email() -> str:
    return f"test-{uuid.uuid4().hex[:8]}@exemple.fr"


def test_password_is_hashed():
    hashed = hash_password("motdepasse123")
    assert hashed != "motdepasse123"
    assert verify_password("motdepasse123", hashed)
    assert not verify_password("mauvais", hashed)


def test_register_then_login_then_me():
    email = unique_email()
    assert client.post("/auth/register",
                       json={"email": email, "password": "motdepasse123"}).status_code == 201
    token = client.post("/auth/login",
                        json={"email": email, "password": "motdepasse123"}).json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == email


def test_duplicate_email_is_refused():
    email = unique_email()
    client.post("/auth/register", json={"email": email, "password": "motdepasse123"})
    again = client.post("/auth/register", json={"email": email.upper(), "password": "autre12345"})
    assert again.status_code == 409


def test_wrong_password_is_refused():
    email = unique_email()
    client.post("/auth/register", json={"email": email, "password": "motdepasse123"})
    assert client.post("/auth/login",
                       json={"email": email, "password": "mauvais123"}).status_code == 401


def test_short_password_and_bad_email_are_rejected():
    assert client.post("/auth/register",
                       json={"email": unique_email(), "password": "court"}).status_code == 422
    assert client.post("/auth/register",
                       json={"email": "pas-un-email", "password": "motdepasse123"}).status_code == 422


def test_invalid_token_is_refused():
    assert client.get("/auth/me", headers={"Authorization": "Bearer faux"}).status_code == 401