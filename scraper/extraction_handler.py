import logging
from scraper.strategies.shopify.api_strategy import ShopifyAPIBulkStategy
from scraper.strategies.shopify.sitemap_single_product_strategy import (
    ShopifySitemapSingleProductStrategy,
)

from scraper.strategies.bigcommerce.sitemap_single_product_strategy import BigCommerceSitemapSingleProductStrategy
from scraper.strategies.wix.sitemap_single_product_strategy import WixSitemapSingleProductStrategy

from typing import Callable

from scraper.strategies.woocommerce.sitemap_single_product_strategy import WooCommerceSitemapSingleProductStrategy



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
        elif self.vendor == "woocommerce":
            return [WooCommerceSitemapSingleProductStrategy()]
        else:
            raise ValueError(f"Vendor no soportado: {self.vendor}")


    def extract(self, url: str) -> tuple[list, str]:
        last_exception = None
        for strategy in self.strategy_chain:
            try:
                used_strategy_name = strategy.__class__.__name__
                self.logger.info("Seleccionada estrategia `%s`", strategy.__class__.__name__)
                data = strategy.extract(url)
                if data:
                    self.logger.info("Estrategia exitosa: '%s'", used_strategy_name)
                    return data, used_strategy_name
            except Exception as e:
                self.logger.error("¡La estrategia '%s' falló!", used_strategy_name)
                last_exception = e

        raise Exception(
            "Todas las estrategias de extracción fallaron"
        ) from last_exception
