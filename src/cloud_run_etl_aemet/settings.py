from dotenv import load_dotenv
from datetime import timedelta
#from pydantic import Field, BaseSettings
from pydantic_settings import BaseSettings
import os
# Cargar variables de entorno desde el archivo .env
load_dotenv()
# Verifica el valor cargado para MAX_DELTA_TIME
print("MAX_DELTA_TIME:", os.getenv("MAX_DELTA_TIME"))

class Settings(BaseSettings):
    # General params
    project_id: str

    # Connector params
    max_delta_time: int

    # Sink params
    table_name: str
    table_station: str
    dataset_name: str

    # Source params
    init_endpoint: str #= Field(alias="INIT_ENDPOINT")

    #api key
    api_key: str 
    @property
    def max_delta_time_timedelta(self):
        return timedelta(days=self.max_delta_time)

settings = Settings()  # type: ignore
#settings = Settings(SettingsConfigDict(env_file=".env"))  # type: ignore
