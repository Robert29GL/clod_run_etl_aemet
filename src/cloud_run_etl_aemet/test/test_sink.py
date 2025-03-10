from unittest.mock import  MagicMock
from google.cloud.exceptions import NotFound

from cloud_run_etl_aemet.sink import BigQuerySink

def test_create_table_if_not_exists_stg_new_table(mocker):
    mock_client = MagicMock()
    mock_client.get_table.side_effect = NotFound("Table not found")
    mocker.patch("google.cloud.bigquery.Client", return_value=mock_client)

    sink = BigQuerySink()
    sink.create_table_if_not_exists_stg()

    mock_client.create_table.assert_called_once()

def test_create_table_if_not_exists_stg_existing_table(mocker):
    mock_client = MagicMock()
    mocker.patch("google.cloud.bigquery.Client", return_value=mock_client)

    sink = BigQuerySink()
    sink.create_table_if_not_exists_stg()

    mock_client.create_table.assert_not_called()

def test_insert_rows_stg_success(mocker):
    mock_client = MagicMock()
    mocker.patch("google.cloud.bigquery.Client", return_value=mock_client)

    sink = BigQuerySink()
    records = [{"fecha": "2023-01-01", "indicativo": "1234X", "nombre": "Estacion X", "altitud": "100", "tmed":"10.0"}]
    sink.insert_rows_stg(records)

    mock_client.insert_rows_json.assert_called_once()

def test_insert_rows_stg_error(mocker):
    mock_client = MagicMock()
    mock_client.insert_rows_json.return_value = [{"errors": "some errors"}]
    mocker.patch("google.cloud.bigquery.Client", return_value=mock_client)

    sink = BigQuerySink()
    records = [{"fecha": "2023-01-01", "indicativo": "1234X", "nombre": "Estacion X", "bad_key": "bad_value"}]
    sink.insert_rows_stg(records)

    mock_client.insert_rows_json.assert_called_once()