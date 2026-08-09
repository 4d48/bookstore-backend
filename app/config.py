from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config: SettingsConfigDict = SettingsConfigDict(  # pyright: ignore[reportIncompatibleVariableOverride]
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    SQLALCHEMY_DATABASE_URL: str


settings = Settings()  # pyright: ignore[reportCallIssue]
