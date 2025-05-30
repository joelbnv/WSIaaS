import csv
import json
from datetime import date, datetime
from typing import Iterable, List, Optional

import pyarrow as pa
import pyarrow.parquet as pq
from openpyxl import Workbook
from pydantic import BaseModel, HttpUrl

from database.databases import MySQLDB, PostgreSQLDB, SQLiteDB
from transformer.transformer_handler import Product


class ShopifyProductVariant(BaseModel):
    variant_id: int
    product_id: int
    product_title: str
    vendor: str
    product_type: str
    handle: str
    variant_title: str
    price: float
    currency: str
    weight: float
    weight_unit: str
    inventory_quantity: int
    requires_shipping: bool
    image_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_json(cls, product: dict, variant: dict, image_url: Optional[str] = "") -> "ShopifyProductVariant":
        return cls(
            variant_id=variant.get("id", 0),
            product_id=product.get("id", 0),
            product_title=product.get("title", ""),
            vendor=product.get("vendor", ""),
            product_type=product.get("product_type", ""),
            handle=product.get("handle", ""),
            variant_title=variant.get("title", ""),
            price=float(variant.get("price", 0)),
            currency=variant.get("price_currency", "USD"),
            weight=float(variant.get("weight", 0)),
            weight_unit=variant.get("weight_unit", ""),
            inventory_quantity=variant.get("inventory_quantity", 0),
            requires_shipping=variant.get("requires_shipping", False),
            image_url=image_url or "",
            created_at=variant.get("created_at", datetime.utcnow()),
            updated_at=variant.get("updated_at", datetime.utcnow())
        )


class ShopifyProduct(BaseModel):
    product_id: int
    title: str
    vendor: str
    product_type: str
    handle: str
    image_url: Optional[str]
    tags: Optional[str]

    variants: List[ShopifyProductVariant]

    @staticmethod
    def from_json(data: dict) -> List[ShopifyProductVariant]:
        """Flattens Shopify product JSON into one product per variant"""
        product = data.get("product", {})
        image_url = product.get("image", {}).get("src", "")
        variants = product.get("variants", [])

        return [
            ShopifyProductVariant.from_json(product, variant, image_url)
            for variant in variants
        ]

    @staticmethod
    def from_json_bulk_api(payload: dict) -> List[ShopifyProductVariant]:
        all_variants = []
        for product in payload.get("products", []):
            all_variants.extend(ShopifyProduct.from_json(product))
        return all_variants


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