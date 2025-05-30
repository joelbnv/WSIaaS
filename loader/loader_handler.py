import pandas as pd
import csv
import os
import json
from database.db_factory import DatabaseFactory
from transformer.input_mappers_pydantic.bigcommerce import BigCommerceProduct
from transformer.input_mappers_pydantic.prestashop import PrestashopProduct
from transformer.input_mappers_pydantic.shopify import ShopifyProduct
from transformer.input_mappers_pydantic.wix import WixProduct
from transformer.input_mappers_pydantic.woocommerce import WooCommerceProduct
from transformer.transformer_handler import Product
from typing import Iterable


"""
"data" should be a list of validated pydantic models, and it should not involve pandas at all.
The logic for dealing with iterables of pydantic models and writing them in batches is defined
within the pydantic models themselves. 
"""


class LoaderHandler:
    def __init__(self, data: Iterable[Product], destination_format: str, vendor: str, db_config: dict | str = None):
        self.data = data
        self.destination_format = destination_format
        self.vendor = vendor
        self.db_config = json.loads(db_config) if isinstance(db_config, str) else db_config

    def load(self) -> None:

        if self.destination_format == "csv":

            if self.vendor == "shopify":
                ShopifyProduct.write_batch_csv(self.data, path=None)
            elif self.vendor == "bigcommerce":
               BigCommerceProduct.write_batch_csv(self.data, path=None)
            elif self.vendor == "wix":
                WixProduct.write_batch_csv(self.data, path=None)
            elif self.vendor == "prestashop":
                PrestashopProduct.write_batch_csv(self.data, path=None)
            elif self.vendor == "woocommerce":
                WooCommerceProduct.write_batch_csv(self.data, path=None)

        elif self.destination_format == "json":

            if self.vendor == "shopify":
                ShopifyProduct.write_batch_json(self.data, path=None)
            elif self.vendor == "bigcommerce":
                BigCommerceProduct.write_batch_json(self.data, path=None)
            elif self.vendor == "wix":
                WixProduct.write_batch_json(self.data, path=None)
            elif self.vendor == "prestashop":
                PrestashopProduct.write_batch_json(self.data, path=None)
            elif self.vendor == "woocommerce":
                WooCommerceProduct.write_batch_json(self.data, path=None)


        elif self.destination_format == "jsonl":

            if self.vendor == "shopify":
                ShopifyProduct.write_batch_jsonl(self.data, path=None)
            elif self.vendor == "bigcommerce":
                BigCommerceProduct.write_batch_jsonl(self.data, path=None)
            elif self.vendor == "wix":
                WixProduct.write_batch_jsonl(self.data, path=None)
            elif self.vendor == "prestashop":
                PrestashopProduct.write_batch_jsonl(self.data, path=None)
            elif self.vendor == "woocommerce":
                WooCommerceProduct.write_batch_jsonl(self.data, path=None)

        elif self.destination_format == "excel":

            if self.vendor == "shopify":
                ShopifyProduct.write_batch_excel(self.data, path=None)
            elif self.vendor == "bigcommerce":
                BigCommerceProduct.write_batch_excel(self.data, path=None)
            elif self.vendor == "wix":
                WixProduct.write_batch_excel(self.data, path=None)
            elif self.vendor == "prestashop":
                PrestashopProduct.write_batch_excel(self.data, path=None)
            elif self.vendor == "woocommerce":
                WooCommerceProduct.write_batch_excel(self.data, path=None)

        elif self.destination_format == "parquet":

            if self.vendor == "shopify":
                ShopifyProduct.write_batch_parquet(self.data, path=None)
            elif self.vendor == "bigcommerce":
                BigCommerceProduct.write_batch_parquet(self.data, path=None)
            elif self.vendor == "wix":
                WixProduct.write_batch_parquet(self.data, path=None)
            elif self.vendor == "prestashop":
                PrestashopProduct.write_batch_parquet(self.data, path=None)
            elif self.vendor == "woocommerce":
                WooCommerceProduct.write_batch_parquet(self.data, path=None)

        elif self.destination_format == "sqlite":

            if self.vendor == "shopify":
                ShopifyProduct.write_batch_sqlite(self.data, path=None)
            elif self.vendor == "bigcommerce":
                BigCommerceProduct.write_batch_sqlite(self.data, path=None)
            elif self.vendor == "wix":
                WixProduct.write_batch_sqlite(self.data, path=None)
            elif self.vendor == "prestashop":
                PrestashopProduct.write_batch_sqlite(self.data, path=None)
            elif self.vendor == "woocommerce":
                WooCommerceProduct.write_batch_sqlite(self.data, path=None)

        elif self.destination_format == "mysql":

            if self.vendor == "shopify":
                ShopifyProduct.write_batch_mysql(self.data, path=None)
            elif self.vendor == "bigcommerce":
                BigCommerceProduct.write_batch_mysql(self.data, path=None)
            elif self.vendor == "wix":
                WixProduct.write_batch_mysql(self.data, path=None)
            elif self.vendor == "prestashop":
                PrestashopProduct.write_batch_mysql(self.data, path=None)
            elif self.vendor == "woocommerce":
                WooCommerceProduct.write_batch_mysql(self.data, path=None)

        elif self.destination_format == "postgres":

            if self.vendor == "shopify":
                ShopifyProduct.write_batch_postgres(self.data, path=None)
            elif self.vendor == "bigcommerce":
                BigCommerceProduct.write_batch_postgres(self.data, path=None)
            elif self.vendor == "wix":
                WixProduct.write_batch_postgres(self.data, path=None)
            elif self.vendor == "prestashop":
                PrestashopProduct.write_batch_postgres(self.data, path=None)
            elif self.vendor == "woocommerce":
                WooCommerceProduct.write_batch_postgres(self.data, path=None)