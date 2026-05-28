"""
Configurazione centralizzata dell'applicazione.

Carica variabili d'ambiente da .env
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurazione principale dell'applicazione.
    
    Le variabili vengono caricate da:
    1. File .env nella radice del progetto
    2. Variabili d'ambiente del sistema
    """
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # 🔧 API Configuration
    gemini_api_key: str

    # 🔐 JWT Security Configuration
    secret_key: str = "your-secret-key-change-in-production-min-256-bits"
    algorithm: str = "HS256"

    # 🐘 PostgreSQL Database URL (formato moderno)
    # Formato: postgresql+psycopg://user:password@host:port/database
    database_url: str

    # 🚦 Rate Limiting Configuration
    # For authenticated users
    auth_rate_limit: int = 5
    auth_time_window_seconds: int = 60

    # For unauthenticated "global" users
    global_rate_limit: int = 3
    global_time_window_seconds: int = 60


settings = Settings()
