import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str = os.getenv("DB_URL")
    db_echo: bool = True

setting = Settings()