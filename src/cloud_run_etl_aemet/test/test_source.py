from datetime import datetime
import pytest
from unittest.mock import patch

from cloud_run_etl_aemet.source import aemet_extract_data
from aemet import Estacion



class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

def test_get_stations_success(mocker):
    mock_stations = [{"indicativo": "1234X", "nombre": "Estacion X"}, {"indicativo": "5678Y", "nombre": "Estacion Y"}]
    mocker.patch.object(Estacion, 'get_estaciones', return_value=mock_stations)

    result = aemet_extract_data.get_stations()

    assert result == [{"indicativo": "1234X", "nombre": "Estacion X"}, {"indicativo": "5678Y", "nombre": "Estacion Y"}]

def test_get_stations_failure(mocker):
    mocker.patch.object(Estacion, 'get_estaciones', return_value=None)

    with pytest.raises(Exception):
        aemet_extract_data.get_stations()

def test_extract_object_success(mocker):
    mock_response_1 = MockResponse({"datos": "http://mock_data_url"}, 200)
    mock_response_2 = MockResponse([{"fecha": "2025-01-01", "indicativo": "1234X", "nombre": "Estacion X"}], 200)
    mocker.patch('requests.get', side_effect=[mock_response_1, mock_response_2])

    extract_data = aemet_extract_data()
    start_datetime = datetime(2025, 1, 1)
    end_datetime = datetime(2025, 1, 2)
    result = extract_data.extract_object("1234X", start_datetime, end_datetime)

    assert result == [{"fecha": "2025-01-01", "indicativo": "1234X", "nombre": "Estacion X"}]

def test_extract_object_api_error(mocker):
    mock_response = MockResponse({}, 500)
    mocker.patch('requests.get', return_value=mock_response)

    extract_data = aemet_extract_data()
    start_datetime = datetime(2025, 1, 1)
    end_datetime = datetime(2025, 1, 2)

    with pytest.raises(Exception):
        extract_data.extract_object("1234X", start_datetime, end_datetime)

def test_extract_object_no_data_key(mocker):
    mock_response = MockResponse({}, 200)
    mocker.patch('requests.get', return_value=mock_response)

    extract_data = aemet_extract_data()
    start_datetime = datetime(2025, 1, 1)
    end_datetime = datetime(2025, 1, 2)

    with pytest.raises(Exception):
        extract_data.extract_object("1234X", start_datetime, end_datetime)