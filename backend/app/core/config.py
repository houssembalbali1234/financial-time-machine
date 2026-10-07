"""Configuration de l'application, lue depuis le fichier .env."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://ftm:ftm_dev_password@localhost:5433/ftm"
    # Clé qui signe les jetons de connexion. À remplacer par une longue valeur secrète en production.
    secret_key: str = "dev-secret-a-changer"
    access_token_minutes: int = 60 * 24   # un jeton reste valable 24 heures

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()