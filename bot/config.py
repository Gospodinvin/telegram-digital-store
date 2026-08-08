from pydantic_settings import BaseSettings
from pydantic import SecretStr

class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    ADMIN_IDS: list[int] = []
    DATABASE_URL: str = "sqlite:///./store.db"
    MINI_APP_URL: str = "https://your-miniapp.vercel.app"
    COMMISSION_PERCENT: float = 5.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
