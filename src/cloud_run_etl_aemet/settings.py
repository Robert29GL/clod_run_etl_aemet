
from datetime import timedelta
#from pydantic import Field, BaseSettings
from pydantic_settings import BaseSettings




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
    init_endpoint: str 

    #api key
    api_key: str 
    @property
    def max_delta_time_timedelta(self):
        return timedelta(days=self.max_delta_time)

settings = Settings()  
