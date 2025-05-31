import pandas as pd
import json

from typing import Any, Union, Iterable, Optional, Dict

import itertools

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


    def transform(self, raw_products: Iterable[Dict[str, Any]]) -> Iterable[Product]:
        if self.vendor == "shopify":
            if self.used_extraction_strategy == "ShopifyAPIStrategy":
                """Can be used as-is, does not need transformation"""
                pass

            elif self.used_extraction_strategy == "ShopifySitemapSingleProductStrategy":
                product_list = []

                for x in raw_products:
                    product_list.append(ShopifyProduct.from_json(x))

                # We need to flatten the list, as many products have variants (that are captured as a list
                # of different products, and thus each "variant" is its own product), and they should be
                # processed and stored as different products
                product_list_flattened = list(itertools.chain(*product_list))

                return product_list_flattened

        elif self.vendor == "wix":
            product_list = []
            raw_products_flattened = list(itertools.chain(*raw_products))
            for x in raw_products_flattened:
                product_list.append(WixProduct.from_jsonld(x))
            return product_list

        elif self.vendor == "prestashop":
            product_list = []
            for x in raw_products:
                product_list.append(PrestashopProduct.from_jsonld(x))
            return product_list

        elif self.vendor == "bigcommerce":
            product_list = []
            for x in raw_products:
                product_list.append(BigCommerceProduct.from_json(x))
            return product_list

        elif self.vendor == "woocommerce":
            product_list = []
            for x in raw_products:
                product_list.append(WooCommerceProduct.from_json(x))
            return product_list
            
        else:
            raise ValueError(
                "Transformation Strategy not Supported!! / No transformation strategy was defined"
            )

    def write_to_file(self):
        "Writes the list of Pydantic-validated objects as pickle or any other standard format (jsonl, for example)"
