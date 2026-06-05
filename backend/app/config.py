from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"

    database_url: str = "sqlite:///./speakcoach.db"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
