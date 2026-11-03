from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Configuração da API; o CSV continua sendo a fonte de dados do projeto."""

    model_config = SettingsConfigDict(
        env_prefix="CFTC_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    data_path: Path = BASE_DIR / "dados_dashboard.csv"


settings = Settings()
