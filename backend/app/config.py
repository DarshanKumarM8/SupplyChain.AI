"""
SupplyChainAI — Application Configuration
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Backend
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    debug: bool = True

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://supplychainai:changeme_in_production@localhost:5432/supplychainai"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"

    # Manifold data path
    manifold_data_dir: str = os.path.join(os.path.dirname(__file__), "..", "data", "manifold")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
