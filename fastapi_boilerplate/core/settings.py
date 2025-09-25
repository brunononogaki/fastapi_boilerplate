from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    # Database settings
    database_host: Optional[str] = None
    database_port: Optional[int] = None
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: Optional[str] = None

    # Security settings
    secret_key: str = 'your-secret-key-here-change-in-production'
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30
    admin_password: Optional[str] = None

    # CORS settings
    cors_origins: Optional[str] = None

    @property
    def database_url(self) -> Optional[str]:
        return (
            f'postgresql+psycopg://{self.postgres_user}:{self.postgres_password}'
            f'@{self.database_host}:{self.database_port}/{self.postgres_db}'
        )

    @property
    def cors(self) -> Optional[str]:
        return self.cors_origins.split(',')


settings = Settings()
