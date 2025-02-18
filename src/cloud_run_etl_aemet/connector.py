from datetime import datetime, timedelta
from typing import Protocol
import logging

from cloud_run_etl_aemet.source import aemet_extract_data 
from cloud_run_etl_aemet.settings import settings
from cloud_run_etl_aemet.sink import BigQuerySink

class Source(Protocol):
    def extract_object(
        self,
        station_id: str,
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> list[dict]: ...


class Sink(Protocol):
    def get_last_update_datetime(self, station_id: str) -> datetime: ...

    def load_object(self, station_id: str, data: list[dict]) -> None: ...


class Connector:
    def __init__(
        self,
        source: aemet_extract_data,
        sink: BigQuerySink,
    ) -> None:
        """
        Connector class for extracting and loading data from a source to a sink.
        WORKS WITH UTC TIME ONLY, so make sure to convert to UTC before passing.
        """
        #self.client = logging.Client()
        self.logger = logging.getLogger("cloud_run_etl")
        self.source = source
        self.sink = sink

    def incremental_load(self, station_id: str) -> None:
        """
        Extracts data from the last loaded date up to the current date 
        (or a defined range) for a given station, and inserts the data
        into the stagin table
        """
        start_datetime = (datetime.now() - timedelta(days=15)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_datetime = (datetime.now() - timedelta(days=4)).replace(hour=0, minute=0, second=0, microsecond=0)
        self.extract_and_load_object(station_id, start_datetime, end_datetime)
        

    def extract_and_load_object(self, station_id: str, start_datetime: datetime, end_datetime: datetime) -> None:
        """
        Extrae datos en el rango definido y los carga en el sink.
        """
        self.logger.info(f"Extracting and loading data for station: {station_id} from {start_datetime} to {end_datetime}")
        
        current_start = start_datetime
        while current_start < end_datetime:
            current_end = min(current_start + settings.max_delta_time_timedelta, end_datetime)
            
            records = self.source.extract_object(station_id, current_start, current_end)
            
            if not records:
                self.logger.info(f"No data for {station_id} from {current_start} to {current_end}. Skipping...")
            else:
                self.sink.insert_rows_stg(records)
                self.logger.info(f"Inserted {len(records)} records for {station_id} from {current_start} to {current_end}.")
            
            current_start = current_end  

    # def extract_and_load_object(
    #     self,
    #     station_id: str,
    #     start_datetime: datetime,
    #     end_datetime: datetime,
    # ) -> None:
    #     self.logger.info(
    #         f"Extracting and loading object: {station_id}"
    #         f" from {start_datetime} to {end_datetime}",
    #     )
    #     t0 = start_datetime
    #     while t0 < end_datetime:
    #         t1 = min(t0 + settings.max_delta_time, end_datetime)
    #         df = self.source.extract_object(station_id, t0, t1)
    #         if df.empty:
    #             self.logger.info(
    #                 f"Empty dataframe for {station_id} from {t0} to {t1}. Skipping...",
    #             )
    #         else:
    #             self.sink.load_object(station_id, df)
    #             self.logger.info(f"Wrote dataframe for {station_id}from {t0} to {t1}.")
    #         t0 = t1
