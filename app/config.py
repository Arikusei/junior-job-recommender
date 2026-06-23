from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./data/jobs.db"
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    artifacts_dir: str = "./artifacts"
    ab_control_ratio: float = 0.5
    log_level: str = "INFO"


settings = Settings()
