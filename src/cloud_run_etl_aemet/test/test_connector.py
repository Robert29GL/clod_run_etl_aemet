from unittest.mock import MagicMock
from datetime import datetime, timedelta

from cloud_run_etl_aemet.connector import Connector

def test_extract_and_load_object(mocker):
    mock_source = MagicMock()
    mock_sink = MagicMock()
    mock_source.extract_object.return_value = [{"fecha": "2025-01-01", "indicativo": "1234X", "nombre": "Estacion X"}]

    connector = Connector(mock_source, mock_sink)
    start_datetime = datetime(2025, 1, 1)
    end_datetime = datetime(2025, 1, 2)
    connector.extract_and_load_object("1234X", start_datetime, end_datetime)

    mock_source.extract_object.assert_called_once_with("1234X", start_datetime, end_datetime)
    mock_sink.insert_rows_stg.assert_called_once_with([{"fecha": "2025-01-01", "indicativo": "1234X", "nombre": "Estacion X"}])