"""Configuration de l'application, lue depuis le fichier .env."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://ftm:ftm_dev_password@localhost:5433/ftm"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()