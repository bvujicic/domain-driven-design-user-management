from pathlib import Path
from typing import Optional

from pydantic import BaseSettings


class Configuration(BaseSettings):
    DEBUG: bool
    SECRET_KEY: str
    CORS_ALLOWED_ORIGINS: Optional[list[str]] = ['*']

    DATABASE_URI: str

    JWT_ALGORITHM: str = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRY_IN_SECONDS: int = 86_400
    JWT_CHANGE_TOKEN_EXPIRY_IN_SECONDS: int = 7 * 24 * 3_600

    GOOGLE_CLOUD_STORAGE_CREDENTIALS_PATH: Optional[str]
    GOOGLE_CLOUD_STORAGE_BUCKET_NAME: str

    CUSTOMER_IO_SITE_ID: str = ''
    CUSTOMER_IO_API_KEY: str = ''

    SUPERADMIN_USERNAME: str

    class Config:
        env_file = Path(__file__).parent.parent.parent / '.env'
        env_file_encoding = 'utf-8'


configuration = Configuration()
