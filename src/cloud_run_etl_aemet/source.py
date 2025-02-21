from datetime import datetime
import requests

from typing import  List, Dict
from cloud_run_etl_aemet.settings import settings
from aemet import Estacion

class aemet_extract_data:
    @staticmethod
    def get_stations() -> List[Dict]:
        """Retrieves the list of weather stations and returns a list 
        of dictionaries with 'indicativo' and 'nombre'."""
        stations_json = Estacion.get_estaciones(api_key=settings.api_key)
        if not stations_json:
            raise Exception("Cannot get stations")

        stations = stations_json
        # Filter fields 'indicativo' y 'nombre'
        filter_stations = [
            {'indicativo': estacion['indicativo'], 'nombre': estacion['nombre']}
            for estacion in stations
        ]
        return filter_stations

    def extract_object(
        self,
        station_id: str,
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> List[Dict]:
        # extract weather data from AEMET API
        microbatch_duration = settings.max_delta_time_timedelta
        current_start = start_datetime
        current_end = end_datetime
        all_records: List[Dict] = []

        while current_start < end_datetime:
            current_end = min(current_start + microbatch_duration, end_datetime)
            
            # Construct dynamic URL with parameters
            endpoint_url = (
                f"{settings.init_endpoint}/valores/climatologicos/diarios/datos/"
                f"fechaini/{current_start.strftime('%Y-%m-%dT%H:%M:%SUTC')}/"
                f"fechafin/{current_end.strftime('%Y-%m-%dT%H:%M:%SUTC')}/"
                f"estacion/{station_id}"
            )
            params = {"api_key": settings.api_key}

            # First request: Get the URL for the data
            response = requests.get(endpoint_url, params=params)
            if response.status_code != 200:
                raise Exception(f"Initial request error: {response.status_code} - {response.text}")
            
            json_response = response.json()
            if "datos" not in json_response:
                raise Exception("Key 'datos' not found in AEMET response.")
            data_url = json_response["datos"]  

            # Second request: Extracts the value of the data field from
            #the previous request.
            data_response = requests.get(data_url)
            if data_response.status_code != 200:
                print(f"Error obtaining data: {data_response.status_code} - {data_response.text}")
                current_start = current_end
                continue
            batch_data = data_response.json() 
            all_records.extend(batch_data)

            print(f"Extracted batch from {current_start} to {current_end}")
            current_start = current_end

        return all_records
# limite de llamadas por minuto es de 20 dias por minuto
# This block is only for testing the module directly.
# if __name__ == "__main__":
#     extractor = aemet_extract_data()
#     data = extractor.extract_object(
#         station_id="3195",
#         start_datetime=datetime.fromisoformat("2025-02-02"),
#         end_datetime=datetime.fromisoformat("2025-02-13")
#     )
#     print("Extracted JSON data:")
#     print(data)
