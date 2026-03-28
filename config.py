from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str
    PROVIDER_TOKEN: str
    ADMIN_IDS: List[int]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    @property
    def admin_ids(self) -> List[int]:
        return self.ADMIN_IDS


settings = Settings()