from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    redis_url: str = "redis://localhost:6379/0"
    overpass_url: str = (
        "https://overpass.kumi.systems/api/interpreter,"
        "https://overpass-api.de/api/interpreter,"
        "https://overpass.openstreetmap.ru/api/interpreter"
    )
    overpass_max_retries: int = 2
    overpass_timeout_seconds: float = 60.0
    demo_mode: bool = False
    geoapify_api_key: str = ""
    nominatim_user_agent: str = "optipoint-dev"
    cache_ttl_seconds: int = 86400
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    log_level: str = "INFO"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def overpass_urls(self) -> list[str]:
        return [u.strip() for u in self.overpass_url.split(",") if u.strip()]


settings = Settings()
