from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    br_analytics_base_url: str = "https://brandanalytics.ru"
    br_analytics_login: str = ""
    br_analytics_password: str = ""
    br_analytics_fallback_theme_id: str = "14132452"
    br_analytics_fallback_theme_name: str = "Российская креативная неделя"

    playwright_headless: bool = True
    playwright_timeout_ms: int = 90_000

    database_url: str = "postgresql+asyncpg://tg_monitoring:tg_monitoring@localhost:5432/tg_monitoring"
    api_cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.api_cors_origins.split(",") if origin.strip()]

    @property
    def login_url(self) -> str:
        return f"{self.br_analytics_base_url.rstrip('/')}/account/login/"

    @property
    def summary_url(self) -> str:
        return f"{self.br_analytics_base_url.rstrip('/')}/summary"

    @property
    def create_theme_url(self) -> str:
        return f"{self.br_analytics_base_url.rstrip('/')}/action/create_theme/"

    @property
    def fallback_theme_edit_url(self) -> str:
        theme_id = self.br_analytics_fallback_theme_id
        return f"{self.br_analytics_base_url.rstrip('/')}/action/update_theme/{theme_id}/"


settings = Settings()
