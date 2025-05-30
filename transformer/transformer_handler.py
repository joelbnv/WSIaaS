import pandas as pd
import json

from typing import Any, Union, Iterable, Optional

from transformer.input_mappers_pydantic.shopify import ShopifyProduct
from transformer.input_mappers_pydantic.bigcommerce import BigCommerceProduct
from transformer.input_mappers_pydantic.prestashop import PrestashopProduct
from transformer.input_mappers_pydantic.wix import WixProduct
from transformer.input_mappers_pydantic.woocommerce import WooCommerceProduct


Product = Union[ShopifyProduct, PrestashopProduct, WixProduct, BigCommerceProduct]

class TransformerHandler:
    def __init__(self, vendor: str, used_extraction_strategy: str) -> None:
        self.vendor = vendor.lower()
        self.used_extraction_strategy = used_extraction_strategy


    def transform(self, data: Iterable[Any]) -> Iterable[Product]:
        if self.vendor == "shopify":
            if self.used_extraction_strategy == "ShopifyAPIStrategy":
                """Can be used as-is, does not need transformation"""
                pass

            elif self.used_extraction_strategy == "SitemapSingleProductStrategy":
                product_list = [ShopifyProduct.from_json(x) for x in data]
                return product_list

        elif self.vendor == "prestashop":
            product_list = [PrestashopProduct.from_jsonld(x) for x in data]
            return product_list

        elif self.vendor == "bigcommerce":
            product_list = [BigCommerceProduct.from_json(x) for x in data]
            return product_list

        elif self.vendor == "woocommerce":
            product_list = [WooCommerceProduct.from_json(x) for x in data]
            return product_list
            
        else:
            raise ValueError(
                "Transformation Strategy not Supported!! / No transformation strategy was defined"
            )

    def write_to_file(self):
        "Writes the list of Pydantic-validated objects as pickle or any other standard format (jsonl, for example)"
