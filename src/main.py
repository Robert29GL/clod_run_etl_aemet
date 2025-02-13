from datetime import datetime

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

    # Get the stations data from the API
    stations = aemet_extract_data.get_stations()

    # Insert the stations into BigQuery
    bigquery_sink.insert_stations(stations)

if __name__ == "__main__":
    main()