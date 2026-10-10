"""Configuration de l'application, lue depuis le fichier .env."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://ftm:ftm_dev_password@localhost:5433/ftm"
    # Clé qui signe les jetons de connexion. À remplacer par une longue valeur secrète en production.
    secret_key: str = "dev-secret-a-changer"
    access_token_minutes: int = 60 * 24   # un jeton reste valable 24 heures
    # Intelligence artificielle locale : Llama, servi par Ollama.
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_timeout_seconds: float = 180   # sans carte graphique, une réponse peut prendre du temps

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()