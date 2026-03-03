from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/opensalesclaw"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 30
    cors_origins: list[str] = ["http://localhost:3000"]
    app_name: str = "OpenSalesClaw"

    # ---------------------------------------------------------------------------
    # Seeding
    # ---------------------------------------------------------------------------
    # Always creates the default admin user on startup.
    # Set SEED_DEMO_DATA=true to also populate demo CRM records.
    default_admin_email: str = "admin@opensalesclaw.com"
    default_admin_password: str = "admin"
    seed_demo_data: bool = False

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> object:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


settings = Settings()
