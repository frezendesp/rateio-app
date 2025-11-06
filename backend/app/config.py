from pathlib import Path
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Sistema de Rateio Pessoal"
    api_prefix: str = "/api"
    database_url: str | None = None
    default_split_fernando: float = 0.5
    default_split_spouse: float = 0.5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        project_root = Path(__file__).resolve().parents[2]
        data_dir = project_root / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{(data_dir / 'database.db').as_posix()}"


settings = Settings()
