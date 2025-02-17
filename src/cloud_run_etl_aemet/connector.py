from datetime import datetime, timezone,timedelta
from typing import Protocol

import pandas as pd
from cloudops.logging.google import get_logger
from cloud_run_etl_aemet.source import aemet_extract_data 
from cloud_run_etl_aemet.settings import settings
from cloud_run_etl_aemet.sink import BigQuerySink
sink= BigQuerySink()
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
        source: Source,
        sink: Sink,
    ) -> None:
        """
        Connector class for extracting and loading data from a source to a sink.
        WORKS WITH UTC TIME ONLY, so make sure to convert to UTC before passing.
        """
        self.logger = get_logger(__name__)
        self.source = source
        self.sink = sink

    def incremental_load(self, station_id: str) -> None:
        """
        Extracts data from the last loaded date up to the current date 
        (or a defined range) for a given station, and inserts the data
        into the stagin table
        """
        last_date = self.sink.get_last_update_datetime(station_id)
        if last_date is None:
            # Si no hay datos previos, iniciar con un rango predeterminado
            start_dt = datetime.now(timezone.utc) - settings.max_delta_time
        else:
            start_dt = last_date + timedelta(seconds=1)
        end_dt = datetime.now(timezone.utc)
        
        print(f"Extracting data for station {station_id} from {start_dt} to {end_dt}")
        records = self.extract_and_load_object(station_id, start_dt, end_dt)
        if records:
            self.sink.insert_rows_stg(records)
        else:
            print("No new data to load.")

    def extract_and_load_object(self, station_id: str, start_datetime: datetime, end_datetime: datetime) -> None:
        """
        Extrae datos en el rango definido y los carga en el sink.
        """
        t0 = start_datetime
        while t0 < end_datetime:
            t1 = min(t0 + settings.max_delta_time, end_datetime)
            data = self.source.aemet_extract_data(station_id, t0, t1)  
            if not data:
                self.logger.info(
                    f"Empty data for {station_id} from {t0} to {t1}. Skipping...",
                )
            else:
                self.sink.load_object(station_id, data)
                self.logger.info(f"Wrote data for {station_id} from {t0} to {t1}.")
            t0 = t1        

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
