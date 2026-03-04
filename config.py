from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "telegram_mini_app"
    CORS_ORIGINS: List[str] = ["*"]
    SECRET_KEY: str = "your-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG: bool = False
    ADMIN_IDS: str = ""  # কমা দিয়ে আলাদা করা টেলিগ্রাম আইডি, যেমন "123456789,987654321"

    @property
    def admin_ids_list(self) -> List[int]:
        """ADMIN_IDS স্ট্রিংকে ইন্টিজার লিস্টে রূপান্তর করে"""
        if not self.ADMIN_IDS:
            return []
        return [int(id.strip()) for id in self.ADMIN_IDS.split(",") if id.strip()]

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "env_file_encoding": "utf-8"
    }

settings = Settings()
