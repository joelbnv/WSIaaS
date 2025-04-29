from scraper.strategies.shopify.api_strategy import ShopifyAPIStategy
from scraper.strategies.shopify.sitemap_single_product_strategy import (
    SitemapSingleProductStrategy,
)

import json


class ExtractionHandler:
    def __init__(self, vendor: str) -> None:
        self.vendor = vendor.lower()
        self.strategy_chain = self.get_strategy_chain()

    def get_strategy_chain(self) -> list[callable]:
        if self.vendor == "shopify":
            return [SitemapSingleProductStrategy(), ShopifyAPIStategy()]
        elif self.vendor == "prestashop":
            return []
        elif self.vendor == "bigcommerce":
            return []
        else:
            raise ValueError(f"Vendor no soportado: {self.vendor}")


    def extract(self, url: str) -> tuple[list, str]:
        last_exception = None
        for strategy in self.strategy_chain:
            try:
                used_strategy_name = strategy.__class__.__name__
                print(f"Intentando estrategia: {used_strategy_name}")
                data = strategy.extract(url)
                if data:
                    print(f"Estrategia exitosa: {used_strategy_name}")
                    return data, used_strategy_name
            except Exception as e:
                print(f"La estrategia falló: {used_strategy_name}: {str(e)}")
                last_exception = e

        raise Exception(
            "Todas las estrategias de extracción fallaron"
        ) from last_exception
    
    def dump(self, raw_data, used_strategy_name: str) -> None:
        """Dumps (for now, Shopify API Data) into a JSON file"""

        if self.vendor == "shopify" and used_strategy_name == "ShopifyAPIStrategy":
            with open("extraction_results/result.json", "w") as file: 
                json.dump(raw_data, file, indent=4)

        if self.vendor == "shopify" and used_strategy_name == "SitemapSingleProductStrategy":
            with open("extraction_results/result.json", "w") as file: 
                json.dump(raw_data, file, indent=4)
