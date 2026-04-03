from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_secret_key: str = "change-me"
    api_admin_token: str = "replace-with-token"
    session_encryption_key: str = "replace-with-32-byte-base64-key"
    database_url: str = "sqlite:///./rr_panel.db"
    log_level: str = "INFO"
    cors_allow_origins: str = "*"
    feature_wars_watchlist: bool = True
    feature_telegram: bool = False
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    rr_base_url: str = "https://rivalregions.com"
    perk_interval_minutes: int = 30
    worker_poll_seconds: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
