from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str
    PROVIDER_TOKEN: str
    ADMIN_IDS: str  

    @property
    def admin_ids(self):
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",")]


settings = Settings()