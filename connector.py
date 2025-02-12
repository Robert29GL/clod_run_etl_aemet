from datetime import datetime, timezone
from typing import Protocol

import pandas as pd
from cloudops.logging.google import get_logger

from cloud_run_etl_template.settings import settings


class Source(Protocol):
    def extract_object(
        self,
        object_id: str,
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> pd.DataFrame: ...


class Sink(Protocol):
    def get_last_update_datetime(self, object_id: str) -> datetime: ...

    def load_object(self, object_id: str, df: pd.DataFrame) -> None: ...


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

    def incremental_load(self, object_id: str) -> None:
        start_datetime = self.sink.get_last_update_datetime(object_id)
        end_datetime = datetime.now(timezone.utc)
        self.extract_and_load_object(object_id, start_datetime, end_datetime)

    def extract_and_load_object(
        self,
        object_id: str,
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> None:
        self.logger.info(
            f"Extracting and loading object: {object_id}"
            f" from {start_datetime} to {end_datetime}",
        )
        t0 = start_datetime
        while t0 < end_datetime:
            t1 = min(t0 + settings.max_delta_time, end_datetime)
            df = self.source.extract_object(object_id, t0, t1)
            if df.empty:
                self.logger.info(
                    f"Empty dataframe for {object_id} from {t0} to {t1}. Skipping...",
                )
            else:
                self.sink.load_object(object_id, df)
                self.logger.info(f"Wrote dataframe for {object_id}from {t0} to {t1}.")
            t0 = t1
