from datetime import datetime, timedelta, timezone
import random 
#from cloudops.logging.google import get_logger
from fastapi import FastAPI
from pydantic import BaseModel

#from cloud_run_etl_aemet.connector import Connector
#from cloud_run_etl_aemet.sink import DummySink
#from cloud_run_etl_aemet.source import DummySource
from cloud_run_etl_aemet.source import aemet_extract_data
from cloud_run_etl_aemet.sink import BigQuerySink
#logger = get_logger(__name__)

# app = FastAPI()


# def get_connector() -> Connector:
#     source = aemet_extract_data()
#     sink = BigQuerySink()
#     return Connector(source, sink)


# class IncrementalLoadRequest(BaseModel):
#     object_ids: list[str]


# class BackfillRequest(BaseModel):
#     object_ids: list[str]
#     start_date: datetime
#     end_date: datetime


# @app.post("/incremental_load")
# def process_object_ids(request: IncrementalLoadRequest):
#     connector = get_connector()
#     for object_id in request.object_ids:
#         logger.info(f"Processing object: {object_id}")
#         connector.incremental_load(object_id)


# @app.post("/backfill")
# def backfill(request: BackfillRequest):
#     connector = get_connector()
#     for object_id in request.object_ids:
#         logger.info(f"Processing object: {object_id}")
#         start_datetime = request.start_date
#         end_datetime = request.end_date
#         connector.extract_and_load_object(
#             object_id,
#             start_datetime,
#             end_datetime,
#         )
def main():
    # Create the BigQuerySink object
    bigquery_sink = BigQuerySink()

    # Ensure the table exists
    bigquery_sink.create_table_if_not_exists()
    bigquery_sink.create_table_if_not_exists_stg()    

    # Get the stations data from the API
    stations = aemet_extract_data.get_stations()
    if not stations:
        print("No se encontraron estaciones disponibles.")
        return    

    # Insert the stations into BigQuery
    #bigquery_sink.insert_stations(stations)

        # Seleccionar aleatoriamente una estación para procesar
    if not stations:
        print("No hay estaciones disponibles para procesar.")
        return
    selected_station = random.choice(stations)
    station_id = selected_station["indicativo"]
    print(f"Procesando estación: {station_id} - {selected_station['nombre']}")

    # Definir el rango de fechas (últimos 15 días)
# Establecer las fechas con hora 00:00:00
# Establecer las fechas con hora 00:00:00 en la zona horaria local
    start_datetime = (datetime.now() - timedelta(days=15)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_datetime = (datetime.now() - timedelta(days=4)).replace(hour=0, minute=0, second=0, microsecond=0)


    print(f"start_datetime: {start_datetime}")
    print(f"end_datetime: {end_datetime}")
    #extractor = aemet_extract_data.extract_object()
    weather_data = aemet_extract_data.extract_object(station_id, start_datetime, end_datetime)

    if not weather_data:
        print(f"No se encontraron datos meteorológicos para la estación {station_id}.")
        return

    # Insertar los datos en la tabla daily_weather_stg en BigQuery
    bigquery_sink.insert_rows_stg(weather_data)

    print(f"Datos meteorológicos de la estación {station_id} insertados correctamente en BigQuery.")


if __name__ == "__main__":
    main()