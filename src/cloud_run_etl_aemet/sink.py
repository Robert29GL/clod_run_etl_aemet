# from dateSTRING import dateSTRING
import logging

# import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from cloud_run_etl_aemet.settings import settings
from cloud_run_etl_aemet.utils import convert_to_float

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BigQuerySink:
    def __init__(self):
        self.client = bigquery.Client()
        self.dataset_id = f"{settings.project_id}.{settings.dataset_name}"
        self.table_id = f"{self.dataset_id}.{settings.table_station}"
        self.table_id_stg = f"{self.dataset_id}.{settings.table_name}"

    def create_table_if_not_exists(self):
        """Verifica si la tabla de estaciones existe, y la crea si no."""
        try:
            self.client.get_table(self.table_id)
            logger.info(f"Tabla {self.table_id} ya existe.")
        except NotFound:
            schema = [
                bigquery.SchemaField("indicativo", "STRING"),
                bigquery.SchemaField("nombre", "STRING"),
            ]
            table = bigquery.Table(self.table_id, schema=schema)
            self.client.create_table(table)
            logger.info(f"Tabla {self.table_id} creada.")

    def insert_stations(self, stations):
        """Inserta la lista de estaciones en BigQuery."""
        rows_to_insert = [
            {"indicativo": station["indicativo"], "nombre": station["nombre"]}
            for station in stations
        ]
        errors = self.client.insert_rows_json(self.table_id, rows_to_insert)
        if errors:
            logger.error(f"Errores al insertar estaciones: {errors}")
        else:
            logger.info(f"{len(rows_to_insert)} estaciones insertadas correctamente.")

    def create_table_if_not_exists_stg(self):
        """Verifica si la tabla de datos climáticos existe, y la crea si no."""
        try:
            self.client.get_table(self.table_id_stg)
            logger.info(f"Tabla {self.table_id_stg} ya existe.")
        except NotFound:
            schema = [
                bigquery.SchemaField("fecha", "DATE"),
                bigquery.SchemaField("indicativo", "STRING"),
                bigquery.SchemaField("nombre", "STRING"),
                bigquery.SchemaField("altitud", "INT64"),
                bigquery.SchemaField("tmed", "NUMERIC"),
                bigquery.SchemaField("prec", "NUMERIC"),
                bigquery.SchemaField("tmin", "NUMERIC"),
                bigquery.SchemaField("horatmin", "STRING"),
                bigquery.SchemaField("tmax", "NUMERIC"),
                bigquery.SchemaField("horatmax", "STRING"),
                bigquery.SchemaField("dir", "STRING"),
                bigquery.SchemaField("velmedia", "NUMERIC"),
                bigquery.SchemaField("racha", "NUMERIC"),
                bigquery.SchemaField("horaracha", "STRING"),
                bigquery.SchemaField("presMax", "NUMERIC"),
                bigquery.SchemaField("horaPresMax", "STRING"),
                bigquery.SchemaField("presMin", "NUMERIC"),
                bigquery.SchemaField("horaPresMin", "STRING"),
                bigquery.SchemaField("hrMedia", "INT64"),
                bigquery.SchemaField("hrMax", "INT64"),
                bigquery.SchemaField("horaHrMax", "STRING"),
                bigquery.SchemaField("hrMin", "INT64"),
                bigquery.SchemaField("horaHrMin", "STRING"),
            ]
            table = bigquery.Table(self.table_id_stg, schema=schema)
            self.client.create_table(table)
            logger.info(f"Tabla {self.table_id_stg} creada.")

    def insert_rows_stg(self, all_records):
        """Inserta registros climáticos en la tabla staging de BigQuery."""
        rows_to_insert = []
        for data in all_records:
            try:
                row = {
                    "fecha": data["fecha"],
                    "indicativo": data["indicativo"],
                    "nombre": data["nombre"],
                    "altitud": int(data["altitud"]) if data.get("altitud") else None,
                    "tmed": convert_to_float(data["tmed"])
                    if data.get("tmed")
                    else None,
                    "prec": convert_to_float(data["prec"])
                    if data.get("prec")
                    else None,
                    "tmin": convert_to_float(data["tmin"])
                    if data.get("tmin")
                    else None,
                    "horatmin": data.get("horatmin", None),
                    "tmax": convert_to_float(data["tmax"])
                    if data.get("tmax")
                    else None,
                    "horatmax": data.get("horatmax", None),
                    "dir": data.get("dir", None),  
                    "velmedia": convert_to_float(data["velmedia"])
                    if data.get("velmedia")
                    else None,
                    "racha": convert_to_float(data["racha"])
                    if data.get("racha")
                    else None,
                    "horaracha": data.get("horaracha", None),
                    "presMax": convert_to_float(data.get("presMax", None))
                    if data.get("presMax", None)
                    else None,
                    "horaPresMax": data.get("horaPresMax", None),
                    "presMin": convert_to_float(data.get("presMin", None))
                    if data.get("presMin", None)
                    else None,
                    "horaPresMin": data.get("horaPresMin", None),
                    "hrMedia": int(data["hrMedia"]) if data.get("hrMedia") else None,
                    "hrMax": int(data["hrMax"]) if data.get("hrMax") else None,
                    "horaHrMax": data.get("horaHrMax", None),
                    "hrMin": int(data["hrMin"]) if data.get("hrMin") else None,
                    "horaHrMin": data.get("horaHrMin", None),
                }
                rows_to_insert.append(row)
            except Exception as e:
                logger.error(f"Error procesando fila: {data} - {str(e)}")

        if rows_to_insert:
            errors = self.client.insert_rows_json(self.table_id_stg, rows_to_insert)
            if errors:
                logger.error(f"Errores al insertar filas en staging: {errors}")
            else:
                logger.info(
                    f"{len(rows_to_insert)} registros insertados correctamente en staging."
                )
        else:
            logger.info("No se insertaron registros en staging.")
