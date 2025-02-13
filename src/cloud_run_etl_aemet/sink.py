from datetime import datetime

import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from cloud_run_etl_aemet.settings import settings


# class DummySink:
#     def get_last_update_datetime(self, object_id: str) -> datetime:
#         # Return a dummy datetime
#         return datetime(2021, 1, 1, 0, 0, 0)

#     def load_object(self, object_id: str, df: pd.DataFrame) -> None:
#         # Store data in the table
#         _table_name = settings.table_name

class BigQuerySink:
    def __init__(self):
        self.client = bigquery.Client()
        self.dataset_id = f"{settings.project_id}.{settings.dataset_name}"
        self.table_id = f"{self.dataset_id}.{settings.table_station}"

    def create_table_if_not_exists(self):
        # Verificar si la tabla existe
        try:
            self.client.get_table(self.table_id)
            print(f"Tabla {self.table_id} ya existe.")
        except NotFound:
            # Definir el esquema de la tabla
            schema = [
                bigquery.SchemaField("indicativo", "STRING"),
                bigquery.SchemaField("nombre", "STRING"),
            ]
            # Configurar la tabla
            table = bigquery.Table(self.table_id, schema=schema)
            # Crear la tabla
            self.client.create_table(table)
            print(f"Tabla {self.table_id} creada.")

    def insert_stations(self, stations):
        rows_to_insert = [
            {"indicativo": station["indicativo"], "nombre": station["nombre"]}
            for station in stations
        ]
        errors = self.client.insert_rows_json(self.table_id, rows_to_insert)
        if errors:
            print(f"Errores al insertar filas: {errors}")
        else:
            print(f"{len(rows_to_insert)} filas insertadas correctamente.")