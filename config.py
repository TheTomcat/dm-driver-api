import pathlib
from functools import lru_cache

from pydantic_settings import BaseSettings

ROOT = pathlib.Path(__file__).resolve()


class Settings(BaseSettings):
    JWT_SECRET: str = "TEST_SECRET_DO_NOT_USE_IN_PROD"
    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 8
    DATABASE_URL: str = "sqlite:///db.sqlite"

    FIRST_SUPERUSER: str = "test@example.com"
    FIRST_SUPERUSER_PW: str = "test"

    # DATABASE_URL: PostgresDsn

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    PROFILE_QUERIES: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()  # type: ignore
    # if (test_mode := getenv('TEST')) is not None:

    return settings


# @lru_cache
# def get_settings() -> Settings:
#     settings = Settings()
#     if (db := getenv("POSTGRES_DB")) is not None:
#         settings.DATABASE_URL = PostgresDsn.build(
#             scheme="postgresql",
#             user=settings.DATABASE_URL.user,
#             password=settings.DATABASE_URL.password,
#             host=settings.DATABASE_URL.host,
#             port=settings.DATABASE_URL.port,
#             path=f"/{db}",
#         )
#     return settings#     return settings