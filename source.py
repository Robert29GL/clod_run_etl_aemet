from datetime import datetime, timedelta

import pandas as pd
from typing import TypedDict, List

from cloud_run_etl_aemet.settings import settings
from aemet import Aemet
aemet_client = Aemet(api_key=settings.api_key)

class AemetRecord(TypedDict):
    date: str
    temperature: float
    humed: float

class aemet_extract_data:
    def extract_object(
        self,
        object_id: str,
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> List[AemetRecord]:
        # Call endpoint
        _endpoint = settings.endpoint
        microbatch_duration = timedelta(days=1)
        current_start = start_datetime
        all_records: List[AemetRecord] = []

        while current_start < end_datetime:
            current_end = min(current_start + microbatch_duration, end_datetime)
            
            # Call the API (adjust the method get_data according to the aemet library)
            response = aemet_client.get_data(
                endpoint=_endpoint,
                object_id=object_id,
                start_datetime=current_start.isoformat(),
                end_datetime=current_end.isoformat()
            )
            
            # For debugging: print the API response for each microbatch
            print(f"Batch {current_start} to {current_end}: {response}")
            
            # Assume the API response is a dict with a key "data" containing a list of records.
            batch_records: List[AemetRecord] = response.get("data", [])
            all_records.extend(batch_records)
            
            current_start = current_end

        return all_records
    
if __name__ == "__main__":
    
    object_id = settings.project_id  
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 3)

    extractor = aemet_extract_data()
    records = extractor.extract_data(object_id, start_date, end_date)
    
    print("Extracted data:")
    print(records)