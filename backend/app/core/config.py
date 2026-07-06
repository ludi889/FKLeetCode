from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

def find_project_root(markers: List[str] = [".git", ".project-root"]) -> Path:
    """Walk up from this file until a directory containing `marker` is found."""
    path = Path(__file__).resolve()
    for parent in path.parents:
        if any((parent / marker).exists() for marker in markers):
            return parent
    raise RuntimeError(f"Could not find project root (looking for '{markers}')")


BASE_DIR = find_project_root()


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    ollama_base_url: str
    llm_provider: str
    embeddings_provider: str
    eval_provider: str
    llm_model: str
    embeddings_model: str
    eval_model: str
    llm_api_key: Optional[str] = None
    embeddings_api_key: Optional[str] = None
    eval_api_key: Optional[str] = None
    postgres_host: str = "localhost"
    postgres_port: int = 5432


    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()