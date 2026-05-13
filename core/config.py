from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    DATABASE_URL: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()