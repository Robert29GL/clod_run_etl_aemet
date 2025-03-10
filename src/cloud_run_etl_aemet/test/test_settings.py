from datetime import timedelta
import os

from cloud_run_etl_aemet.settings import Settings, settings

def test_settings_load_env():
    os.environ["PROJECT_ID"] = "test_project"
    os.environ["MAX_DELTA_TIME"] = "10"
    os.environ["TABLE_NAME"] = "test_table"
    os.environ["TABLE_STATION"] = "test_station"
    os.environ["DATASET_NAME"] = "test_dataset"
    os.environ["INIT_ENDPOINT"] = "http://test_endpoint"
    os.environ["API_KEY"] = "test_api_key"

    s = Settings()

    assert s.project_id == "test_project"
    assert s.max_delta_time == 10
    assert s.table_name == "test_table"
    assert s.table_station == "test_station"
    assert s.dataset_name == "test_dataset"
    assert s.init_endpoint == "http://test_endpoint"