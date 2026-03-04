import json

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/opensalesclaw"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 30
    # Stored as a plain string so pydantic-settings never attempts json.loads().
    # Accepts a JSON array ('{"origins": [...]}') or comma-separated origins.
    cors_origins: str = "http://localhost:3000"
    app_name: str = "OpenSalesClaw"

    # ---------------------------------------------------------------------------
    # Seeding
    # ---------------------------------------------------------------------------
    # Always creates the default admin user on startup.
    # Set SEED_DEMO_DATA=true to also populate demo CRM records.
    default_admin_email: str = "admin@opensalesclaw.com"
    default_admin_password: str = "admin"
    seed_demo_data: bool = False

    # ---------------------------------------------------------------------------
    # Registration
    # ---------------------------------------------------------------------------
    # Set to False to disable the open /api/auth/register endpoint. When
    # disabled, new users must be created by a superuser via POST /api/users.
    allow_public_registration: bool = True

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse *cors_origins* into a list of origin strings.

        Supports:
        - JSON array:  '["http://localhost:3000","http://localhost:5173"]'
        - Comma-separated: 'http://localhost:3000,http://localhost:5173'
        - Single origin: 'http://localhost:3000'
        - Empty string:  '' → []
        """
        raw = self.cors_origins.strip()
        if not raw:
            return []
        if raw.startswith("["):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(o) for o in parsed]
            except (json.JSONDecodeError, ValueError):
                pass
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


settings = Settings()
