from typing import List, Optional, Union

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    # Database settings
    database_host: Optional[str] = None
    database_port: Optional[int] = None
    database_user: Optional[str] = None
    database_password: Optional[str] = None
    database_name: Optional[str] = None
    database_name_test: Optional[str] = None

    # Security settings
    secret_key: str = 'your-secret-key-here-change-in-production'
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30
    admin_password: Optional[str] = None

    # Environment
    environment: str = 'development'

    # CORS settings (accept str or list from env)
    cors_origins: Union[List[str], str, None] = [
        'http://localhost:3000',
        'http://localhost:5173',
        'http://localhost:5174',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:5174',
        'http://localhost:8080',
        'http://127.0.0.1:8080',
    ]

    @property
    def database_url(self) -> Optional[str]:
        if not all([
            self.database_host,
            self.database_port,
            self.database_user,
            self.database_password,
            self.database_name,
        ]):
            return None
        return (
            f'postgresql+psycopg://{self.database_user}:{self.database_password}'
            f'@{self.database_host}:{self.database_port}/{self.database_name}'
        )

    @property
    def database_url_test(self) -> Optional[str]:
        if not all([
            self.database_host,
            self.database_port,
            self.database_user,
            self.database_password,
            self.database_name_test,
        ]):
            return None
        return (
            f'postgresql+psycopg://{self.database_user}:{self.database_password}'
            f'@{self.database_host}:{self.database_port}/{self.database_name_test}'
        )


settings = Settings()
