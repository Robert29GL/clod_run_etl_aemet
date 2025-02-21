# clod_run_etl_aemet
The aim of this project is to extract data from the Aemet API and ingest the data into a big query target table.

First, a call is made to the AEMET API to extract the ID_STATION of each station.
Then a second call is made to the API to pass it as an input argument:
- api_key (it is defined as an environment variable in the .env file).
- start date. the last 13 days
- end date (4 days less than the current day, as the api usually gives error when querying current information)
- Id_station (extracted from the first AEMET API call)

A third request is made to extract the url of the DATA field.
This url contains the necessary meteorological data information for each ID_station.

The result is ingested into a big query staggin table called daily_weather_stg.