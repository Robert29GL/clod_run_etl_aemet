from datetime import timedelta

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # General params
    project_id: str

    # Connector params
    max_delta_time: timedelta

    # Sink params
    table_name: str

    # Source params
    endpoint: str

    #api key
    api_key: str


settings = Settings()  # type: ignore
