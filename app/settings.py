from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, field_validator


class OpenAISettings(BaseSettings):
    model_config = SettingsConfigDict(
        title="OpenAI Settings",
        env_file="../.env",
        env_file_encoding="utf-8",
    )

    OPENAI_API_KEY: str


class DbSettings(BaseSettings):
    model_config = SettingsConfigDict(
        title="DB Settings",
        env_file="../.env",
        env_file_encoding="utf-8",
    )

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_DSN: PostgresDsn | None = None

    @field_validator("POSTGRES_DSN", mode="before")
    @classmethod
    def assemble_db_connection(cls, v, values):
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_HOST"),
            path=f"{values.data.get('POSTGRES_DB') or ''}",
        )


class Settings(BaseSettings):
    DATABASE: DbSettings = DbSettings()
    OPENAI_API_KEY: str = OpenAISettings().OPENAI_API_KEY


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
