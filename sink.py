from datetime import datetime

import pandas as pd

from cloud_run_etl_template.settings import settings


class DummySink:
    def get_last_update_datetime(self, object_id: str) -> datetime:
        # Return a dummy datetime
        return datetime(2021, 1, 1, 0, 0, 0)

    def load_object(self, object_id: str, df: pd.DataFrame) -> None:
        # Store data in the table
        _table_name = settings.table_name
