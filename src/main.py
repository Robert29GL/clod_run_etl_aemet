import logging
import random
from datetime import datetime, timedelta


from pydantic import BaseModel

from cloud_run_etl_aemet.connector import Connector
from cloud_run_etl_aemet.sink import BigQuerySink
from cloud_run_etl_aemet.source import aemet_extract_data

logger = logging.getLogger("cloud_run_etl")
logger.setLevel(logging.INFO)

def get_connector() -> Connector:
    source = aemet_extract_data()
    sink = BigQuerySink()
    return Connector(source, sink)

class IncrementalLoadRequest(BaseModel):
    station_ids: list[str]

# class BackfillRequest(BaseModel):
#     station_ids: list[str]
#     start_date: datetime
#     end_date: datetime

def incremental_load():
    connector = get_connector()

    # get list stations from API
    stations = aemet_extract_data.get_stations()
    if not stations:
        logger.info("Not found available stations.")
        return

    # Ramdomly selecting a station for processing
    selected_station = random.choice(stations)
    station_id = selected_station["indicativo"]
    logger.info(f"Processing station: {station_id} - {selected_station['nombre']}")

    # A date range is set to load in the variable start_datetime the last 15 days.
    # In the variable end_datetime the last 4 days with respect to the current date.
    # The last 4 days are collected, since after several test it is detected that the API doesn't return
    # current data in most of the stations.
    start_datetime = (datetime.now() - timedelta(days=15)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_datetime = (datetime.now() - timedelta(days=4)).replace(hour=0, minute=0, second=0, microsecond=0)

    logger.info(f"start_datetime: {start_datetime}")
    logger.info(f"end_datetime: {end_datetime}")

    # Execute incremental load
    connector.incremental_load(station_id)

def backfill(start_date: datetime, end_date: datetime):
    connector = get_connector()

    # get list station from API Aemet
    stations = aemet_extract_data.get_stations()
    if not stations:
        logger.info("Not foun available stations.")
        return

    # Randomly select a station to process
    selected_station = random.choice(stations)
    station_id = selected_station["indicativo"]
    logger.info(f"Processing station: {station_id} - {selected_station['nombre']}")

    logger.info(f"Running backfill for {station_id} of {start_date} to {end_date}")
    connector.extract_and_load_object(station_id, start_date, end_date)

if __name__ == "__main__":
    logger.info("Starting ETL process...")

    # Run incremental load
    incremental_load()