import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "LOCAL")
    LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", "logs/app.log")
    
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days



settings = Settings()
