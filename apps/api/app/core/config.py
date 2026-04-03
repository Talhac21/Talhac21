from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_secret_key: str
    api_admin_token: str
    session_encryption_key: str
    database_url: str
    log_level: str = "INFO"
    feature_wars_watchlist: bool = True
    feature_telegram: bool = False
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
