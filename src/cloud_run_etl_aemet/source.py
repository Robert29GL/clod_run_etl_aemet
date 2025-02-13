from datetime import datetime, timedelta
import requests
import pandas as pd
from typing import TypedDict, List, Dict
from cloud_run_etl_aemet.settings import settings
from aemet import Estacion, Aemet
import json

class aemet_extract_data:
    @staticmethod
    def get_stations() -> List[Dict]:
        """Obtiene la lista de estaciones meteorológicas y devuelve una lista de diccionarios con 'indicativo' y 'nombre'."""
        estaciones_json = Estacion.get_estaciones(api_key=settings.api_key)
        if not estaciones_json:
            raise Exception("No se han podido obtener estaciones")
        # Convertir la cadena JSON a una lista de diccionarios
        estaciones = json.loads(estaciones_json)
        # Filtrar campos 'indicativo' y 'nombre'
        estaciones_filtradas = [
            {'indicativo': estacion['indicativo'], 'nombre': estacion['nombre']}
            for estacion in estaciones
        ]
        return estaciones_filtradas

    def extract_object(
        self,
        station_id: str,
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> List[Dict]:
        # extract weather data from AEMET API
        microbatch_duration = timedelta(days=1)
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
            data_url = json_response["datos"]  # This URL is where the actual data is

            # Second request: Fetch the actual weather data
            data_response = requests.get(data_url)
            if data_response.status_code != 200:
                raise Exception(f"Data request error: {data_response.status_code} - {data_response.text}")
            
            batch_data = data_response.json()  # This should be a list of records (each a dict)
            all_records.extend(batch_data)

            print(f"Extracted batch from {current_start} to {current_end}")
            current_start = current_end

        return all_records
#limite de llamadas por minuto es de 20 dias por minuto
# This block is only for testing the module directly.
# if __name__ == "__main__":
#     extractor = aemet_extract_data()
#     data = extractor.extract_object(
#         station_id="3195",
#         start_datetime=datetime.fromisoformat("2025-01-20"),
#         end_datetime=datetime.fromisoformat("2025-02-04")
#     )
#     print("Extracted JSON data:")
#     print(data)
