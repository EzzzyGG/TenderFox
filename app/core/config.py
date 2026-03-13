from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "TenderFox"

    # DB
    database_url: str = "postgresql+psycopg://tenderfox:tenderfox@postgres:5432/tenderfox"

    # External sources
    gosplan_base_url: str = "https://v2test.gosplan.info/fz44"


settings = Settings()
