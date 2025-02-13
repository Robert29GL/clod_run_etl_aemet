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
        estaciones = Estacion.get_estaciones(api_key=settings.api_key)
        if not estaciones:
            raise Exception("No se han podido obtener estaciones")
        
        # Imprimir el contenido de la respuesta para verificar los datos
        print("Contenido de la respuesta de la API:")
        print(estaciones)
        
        # Filtrar campos 'indicativo' y 'nombre'
        estaciones_filtradas = [
            {'indicativo': estacion['indicativo'], 'nombre': estacion['nombre']}
            for estacion in estaciones
        ]
        return estaciones_filtradas
    
if __name__ == "__main__":
    # Llamar a la función y almacenar el resultado
    estaciones = aemet_extract_data.get_stations()
    
    # Imprimir el resultado
    print("Estaciones obtenidas:")
    print(estaciones)    
