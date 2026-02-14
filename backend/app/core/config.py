import os
from dataclasses import dataclass


@dataclass(slots=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Anti-Gravity API")
    environment: str = os.getenv("ENVIRONMENT", "development")
    dart_api_key: str | None = os.getenv("DART_API_KEY")
    krx_api_key: str | None = os.getenv("KRX_API_KEY")
