from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # -------------------------
    # PostgreSQL
    # -------------------------
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    # -------------------------
    # Redis
    # -------------------------
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    # -------------------------
    # MLflow
    # -------------------------
    MLFLOW_TRACKING_URI: str

    ENVIRONMENT: str = "development"

    # -------------------------
    # OpenRouter
    # -------------------------

    OPENAI_API_KEY: str
    OPENROUTER_API_KEY: str

    GENERATION_MODEL: str
    EMBEDDING_MODEL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()