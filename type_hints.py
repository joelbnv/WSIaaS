from typing import Union
from transformer.input_mappers_pydantic.bigcommerce import BigCommerceProduct
from transformer.input_mappers_pydantic.prestashop import PrestashopProduct
from transformer.input_mappers_pydantic.shopify import ShopifyProduct
from transformer.input_mappers_pydantic.wix import WixProduct

Product = Union[ShopifyProduct, PrestashopProduct, WixProduct, BigCommerceProduct]
