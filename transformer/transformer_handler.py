
from typing import Any, Union, Iterable, Dict

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
            # Cada producto debe ir asociado en un diccionario a una estrategia de extracción,
            # por lo que construir (y devolver un diccionario con cada producto y su estrategia de extracción,
            # para así hacer el mapping adecuado con los modelos de Pydantic)
            # Ejemplo: {"url_de_producto": "from_ld_json", "url_de_producto_2": "from_pysoptions_var"}

            product_list = []

            # Cada producto (item) es un diccionario con una lista 
            for item in raw_products:

                extraction_strategy_used = item.get("extraction_strategy_used")
                data = item.get("data")

                if extraction_strategy_used == "from_ld_json":
                    product_list.append(WooCommerceProduct.from_jsonld(data))
                elif extraction_strategy_used == "from_pysoptions_var":
                    product_list.append(WooCommerceProduct.from_pysoptions_var(data))

            return product_list
            
        else:
            raise ValueError(
                "Transformation Strategy not Supported!! / No transformation strategy was defined"
            )

    def write_to_file(self):
        "Writes the list of Pydantic-validated objects as pickle or any other standard format (jsonl, for example)"
