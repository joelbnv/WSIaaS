import csv
import json
from datetime import date
from typing import Iterable, Optional

import pyarrow as pa
import pyarrow.parquet as pq
from openpyxl import Workbook
from pydantic import BaseModel, HttpUrl

from database.databases import MySQLDB, PostgreSQLDB, SQLiteDB
from transformer.transformer_handler import Product


class PrestashopProduct(BaseModel):
    name: str
    description: str
    category: str
    sku: str
    mpn: str
    brand: str
    price: float
    currency: str
    url: HttpUrl
    main_image: Optional[HttpUrl]
    availability: str
    seller: str
    price_valid_until: Optional[date]

    @classmethod
    def from_jsonld(cls, data: dict) -> "PrestashopProduct":
        offers = data.get("offers", {})
        brand = data.get("brand", {})

        # Handle primary image (from top-level 'image') and additional from offers
        main_image = data.get("image", None)

        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            category=data.get("category", ""),
            sku=data.get("sku", ""),
            mpn=data.get("mpn", ""),
            brand=brand.get("name", ""),
            price=float(offers.get("price", 0)),
            currency=offers.get("priceCurrency", "EUR"),
            url=offers.get("url", ""),
            main_image=main_image,
            availability=offers.get("availability", "").split("/")[-1],  # e.g. "InStock"
            seller=offers.get("seller", {}).get("name", ""),
            price_valid_until=offers.get("priceValidUntil", None)
        )


    # Writer methods 
    @staticmethod
    def write_batch_csv(records: Iterable[Product], path: str):
        list_records = list(records)
        if not list_records:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list_records[0].model_dump(mode="python").keys())
            writer.writeheader()
            for record in list_records:
                writer.writerow(record.model_dump(mode="python"))

    @staticmethod
    def write_batch_jsonl(records: Iterable[Product], path: str):
        with open(path, "w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record.model_dump(mode="python"), ensure_ascii=False) + "\n")

    @staticmethod
    def write_batch_excel(records: Iterable[Product], path: str):
        list_records = list(records)
        if not list_records:
            return
        wb = Workbook()
        ws = wb.active
        ws.title = "BigCommerceProducts"
        ws.append(list(list_records[0].model_dump(mode="python").keys()))
        for record in list_records:
            ws.append(list(record.model_dump(mode="python").values()))
        wb.save(path)

    @staticmethod
    def write_batch_parquet(records: Iterable[Product], path: str):
        dict_records: list[dict] = [r.model_dump(mode="python") for r in records]
        table = pa.Table.from_pylist(dict_records)
        pq.write_table(table, path)

    
    @staticmethod
    def write_batch_sqlite(records: Iterable[Product], table: str, db_path: str):
        list_records = list(records)
        if not list_records:
            return

        row = list_records[0].model_dump(mode="python")
        fields = list(row.keys())
        field_list = ", ".join(fields)
        placeholders = ", ".join(["?"] * len(fields))
        values = [tuple(str(v) for v in r.model_dump(mode="python").values()) for r in list_records]

        with SQLiteDB(db_path) as (conn, cursor):
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(f'{f} TEXT' for f in fields)})"
            )
            cursor.executemany(
                f"INSERT INTO {table} ({field_list}) VALUES ({placeholders})", values
            )
            conn.commit()


    
    @staticmethod
    def write_batch_mysql(records: Iterable[Product], table: str, conn_params: dict):
        list_records = list(records)
        if not list_records:
            return

        row = list_records[0].model_dump(mode="python")
        fields = list(row.keys())
        field_list = ", ".join(fields)
        placeholders = ", ".join(["%s"] * len(fields))
        values = [tuple(str(v) for v in r.model_dump(mode="python").values()) for r in list_records]

        with MySQLDB(**conn_params) as (conn, cursor):
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(f'{f} TEXT' for f in fields)})"
            )
            cursor.executemany(
                f"INSERT INTO {table} ({field_list}) VALUES ({placeholders})", values
            )
            conn.commit()



    @staticmethod
    def write_batch_postgres(records: Iterable[Product], table: str, conn_params: dict):
        list_records = list(records)
        if not list_records:
            return

        row = list_records[0].model_dump(mode="python")
        fields = list(row.keys())
        field_list = ", ".join(fields)
        placeholders = ", ".join(["%s"] * len(fields))
        values = [tuple(str(v) for v in r.model_dump(mode="python").values()) for r in list_records]

        with PostgreSQLDB(**conn_params) as (conn, cursor):
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(f'{f} TEXT' for f in fields)})"
            )
            cursor.executemany(
                f"INSERT INTO {table} ({field_list}) VALUES ({placeholders})", values
            )
            conn.commit()