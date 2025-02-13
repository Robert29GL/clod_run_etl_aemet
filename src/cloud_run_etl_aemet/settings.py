from dotenv import load_dotenv
from datetime import timedelta
#from pydantic import Field, BaseSettings
from pydantic_settings import BaseSettings, SettingsConfigDict

import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()


class Settings(BaseSettings):
    # General params
    #project_id: str

    # Connector params
    max_delta_time: timedelta

    # Sink params
    table_name: str
    table_station: str
    dataset_name: str

    # Source params
    init_endpoint: str #= Field(alias="INIT_ENDPOINT")

    #api key
    api_key: str 


settings = Settings()  # type: ignore
#settings = Settings(SettingsConfigDict(env_file=".env"))  # type: ignore
