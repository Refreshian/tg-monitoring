from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    br_analytics_base_url: str = "https://brandanalytics.ru"
    br_analytics_login: str = ""
    br_analytics_password: str = ""
    br_analytics_fallback_theme_id: str = "14166164"
    br_analytics_fallback_theme_name: str = "Энергострой"

    playwright_headless: bool = True
    playwright_timeout_ms: int = 90_000

    # Visitor quote is BA "Регулярно / Ежемесячно" list price minus this ratio (Базовый+).
    price_quote_discount_ratio: float = 0.32
    # Higher discount for entry tariffs Стартовый / Стартовый плюс.
    price_quote_starter_discount_ratio: float = 0.38
    ba_tariffs_cache_days: int = 30

    database_url: str = "postgresql+asyncpg://tg_monitoring:tg_monitoring@localhost:5432/tg_monitoring"
    api_cors_origins: str = "http://localhost:5173"

    # Lead notifications
    leads_email_to: str = "monitoringsystem@bk.ru"
    smtp_host: str = "smtp.mail.ru"
    smtp_port: int = 465
    smtp_username: str = "monitoringsystem@bk.ru"
    smtp_password: str = ""
    smtp_use_tls: bool = True
    smtp_from: str = "monitoringsystem@bk.ru"

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    telegram_api_base: str = "https://api.telegram.org"
    telegram_proxy: str = ""
    telegram_force_ip: str = "149.154.167.220"

    # AITUNNEL (OpenAI-compatible) for BA query normalization
    aitunnel_api_key: str = ""
    aitunnel_base_url: str = "https://api.aitunnel.ru/v1"
    aitunnel_model: str = "auto"
    aitunnel_max_tokens: int = 800

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.api_cors_origins.split(",") if origin.strip()]

    @property
    def smtp_configured(self) -> bool:
        return bool(self.smtp_host and self.smtp_username and self.smtp_password and self.leads_email_to)

    @property
    def telegram_configured(self) -> bool:
        return bool(self.telegram_bot_token and self.telegram_chat_id)

    @property
    def aitunnel_configured(self) -> bool:
        return bool(self.aitunnel_api_key and self.aitunnel_base_url)

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
