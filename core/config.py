import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(".env")


class Settings(BaseSettings):
    db_url: str = os.getenv("DATABASE_URL")
    db_echo: bool = True


setting = Settings()
