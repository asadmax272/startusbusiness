from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # App
    app_name: str = "StartUSBusiness API"
    environment: str = "development"
    frontend_url: str = "http://localhost:3000"
    # Comma-separated list of allowed CORS origins. Include every Vercel
    # domain that will call this API: production + preview pattern.
    allowed_origins: str = "http://localhost:3000"

    # Database
    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/startusbusiness"

    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    google_client_id: str = ""
    google_client_secret: str = ""

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    # Claude API (used server-side only, never exposed to the client)
    anthropic_api_key: str = ""
    ai_model: str = "claude-sonnet-4-6"

    # Storage — Supabase Storage (S3-compatible REST API). If supabase_url
    # is empty, storage.py falls back to local disk for pure local dev.
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    storage_bucket: str = "startusbusiness-documents"
    storage_root: str = "/data/documents"  # local-dev fallback only

    # Email (Resend)
    resend_api_key: str = ""
    email_from_address: str = "StartUSBusiness <notifications@example.com>"

    def allowed_origins_list(self) -> list[str]:
        return [o.strip().rstrip("/") for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()

if settings.environment == "production" and settings.jwt_secret == "change-me-in-production":
    raise RuntimeError(
        "JWT_SECRET is still the default placeholder in a production environment. "
        "Set a real, random JWT_SECRET before starting the app."
    )
