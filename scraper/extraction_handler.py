import logging
from scraper.strategies.shopify.api_strategy import ShopifyAPIBulkStategy
from scraper.strategies.shopify.sitemap_single_product_strategy import (
    ShopifySitemapSingleProductStrategy,
)

from scraper.strategies.bigcommerce.sitemap_single_product_strategy import BigCommerceSitemapSingleProductStrategy
from scraper.strategies.wix.sitemap_single_product_strategy import WixSitemapSingleProductStrategy

from typing import Callable

import json



class ExtractionHandler:
    def __init__(self, vendor: str) -> None:
        self.vendor = vendor.lower()
        self.strategy_chain = self.get_strategy_chain()
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_strategy_chain(self) -> list[Callable]:
        if self.vendor == "shopify":
            return [ShopifySitemapSingleProductStrategy(), ShopifyAPIBulkStategy()]
        # elif self.vendor == "prestashop":
        #     return [PrestashopSingleProductStrategy()]
        elif self.vendor == "bigcommerce":
            return [BigCommerceSitemapSingleProductStrategy()]
        elif self.vendor == "wix":
            return [WixSitemapSingleProductStrategy()]
        elif self.vendor == "bigcommerce":
            return [BigCommerceSitemapSingleProductStrategy()]
        else:
            raise ValueError(f"Vendor no soportado: {self.vendor}")


    def extract(self, url: str) -> tuple[list, str]:
        last_exception = None
        for strategy in self.strategy_chain:
            try:
                used_strategy_name = strategy.__class__.__name__
                print(f"Intentando estrategia: {used_strategy_name}")
                self.logger.info("ExtractionHandler: Seleccionada estrategia `%s`", strategy.__class__.__name__)
                data = strategy.extract(url)
                if data:
                    print(f"Estrategia exitosa: {used_strategy_name}")
                    self.logger.info("Estrategia exitosa: %s", used_strategy_name)
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
            with open("result_files/extraction_results/result.json", "w") as file: 
                json.dump(raw_data, file, indent=4)

        if self.vendor == "shopify" and used_strategy_name == "SitemapSingleProductStrategy":
            with open("result_files/extraction_results/result.json", "w") as file: 
                json.dump(raw_data, file, indent=4)
