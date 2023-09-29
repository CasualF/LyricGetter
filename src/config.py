from pydantic import EmailStr, AnyHttpUrl
from starlette.config import Config
from pydantic_settings import BaseSettings
from typing import Optional, Literal
import os

config = Config(".env")


class Settings(BaseSettings):
    title: str = 'Self learning'
    PROJECT_NAME: str
    ENVIRONMENT: str
    MODE: Literal['DEV', 'TEST', 'PROD']

    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    MEDIA_DIR: str = os.path.join(BASE_DIR.replace('src', ''), 'media')

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    HASHING_ALGORYTHM: str
    SECRET: str
    PERMISSION_PASS: str

    SERVER_HOST: AnyHttpUrl
    USERS_OPEN_REGISTRATION: bool = True

    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str

    TEST_DB_NAME: str
    TEST_DB_USER: str
    TEST_DB_PASS: str
    TEST_DB_HOST: str
    TEST_DB_PORT: str

    REDIS_HOST: str
    REDIS_PORT: str

    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "src/account/email-templates"
    EMAILS_ENABLED: bool = True

    GENIUS_CLIENT_ID: str
    GENIUS_CLIENT_SECRET: str

    class Config:
        env_file = '.env'


settings = Settings()

SHOW_DOCS_ENVIRONMENT = ('local', 'staging')

app_configs = {'title': 'Self learning'}


if settings.ENVIRONMENT not in SHOW_DOCS_ENVIRONMENT:
    app_configs['openapi_url'] = None















