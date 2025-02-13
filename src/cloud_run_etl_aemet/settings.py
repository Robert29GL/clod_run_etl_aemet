from datetime import timedelta
from pydantic import Field, BaseSettings
#from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # General params
    project_id: str

    # Connector params
    max_delta_time: timedelta

    # Sink params
    table_name: str

    # Source params
    init_endpoint: str = Field(alias="INIT_ENDPOINT")

    #api key
    api_key: str = Field(alias="APY_KEY")


settings = Settings()  # type: ignore
