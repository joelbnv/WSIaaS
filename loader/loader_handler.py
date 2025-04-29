import pandas as pd
import csv
import os
import json
from database.db_factory import DatabaseFactory


class LoaderHandler:
    def __init__(self, vendor: str, data, destination_format: str, db_type: str = None, db_config: dict = None) -> None:
        self.vendor = vendor
        self.data = data
        self.destination_format = destination_format
        self.db_type = db_type.lower() if db_type else None
        self.db_config = json.loads(db_config) if isinstance(db_config, str) else db_config
        os.makedirs("result_files/loading_results", exist_ok=True)

    def save_to_json(self, data: dict | pd.DataFrame) -> None:
        if isinstance(data, pd.DataFrame):
            data.to_json(
                "result_files/loading_results/final_results.json", orient="records", indent=4
            )

    def save_to_csv(self, data: dict | pd.DataFrame) -> None:
        if isinstance(data, pd.DataFrame):
            data.to_csv(
                "result_files/loading_results/final_results.csv",
                sep=";",
                encoding="utf-8",
                quoting=csv.QUOTE_ALL,
                index=False
            )

    def save_to_excel(self, data: dict | pd.DataFrame) -> None:
        if isinstance(data, pd.DataFrame):
            data.to_excel("result_files/loading_results/final_results.xlsx", sheet_name="Data")




    def save_to_database(self, data: dict | pd.DataFrame, if_exists="replace", table_name: str = "Products") -> None:
        
        if isinstance(data, dict):
            data = pd.DataFrame([data])

        db_instance = DatabaseFactory.get_database(self.db_type, self.db_config)

        with db_instance as (conn, cursor):

            if if_exists == "replace":
                cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
                # In the future, we might create auxiliary function to adapt 
                columns = ", ".join([f"{col} TEXT" for col in data.columns])
                create_stmt = f"CREATE TABLE {table_name} ({columns});"
                cursor.execute(create_stmt)
                conn.commit()
            
            columns = ", ".join(data.columns)
            placeholders = ", ".join(["%s"] * len(data.columns))

            query = f"INSERT INTO {table_name} ({columns}) ({placeholders})"
            values = [tuple(row) for row in data.itertuples(index=False, name=None)]

            cursor.executemany(query, values)
            conn.commit()

    def load_data_to_destination(self) -> None:
        if self.destination_format == "json":
            self.save_to_json(self.data)
        elif self.destination_format == "csv":
            self.save_to_csv(self.data)
        elif self.destination_format == "excel":
            self.save_to_excel(self.data)
        elif self.destination_format == "sql":
            if not self.db_type or not self.db_config:
                raise ValueError("Debe especificarse el vendor de BBDD y los parámetros de conexión para la BBDD para poder guardar los datos en la BBDD. Abortando!")
            self.save_to_database(self.data)
