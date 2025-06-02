from pydantic import BaseModel, ConfigDict
from typing import Optional


class BigCommerceProduct(BaseModel):
    sku: str
    gtin: str
    mpn: str
    upc: str
    weight: float
    price: float
    currency: str
    sale_price: float
    non_sale_price: float
    in_stock: bool
    out_of_stock_message: Optional[str]
    purchasing_message: Optional[str]
    stock_message: Optional[str]
    purchasable: bool
    out_of_stock_behavior: Optional[str]

    model_config = ConfigDict(frozen=True)

    @classmethod
    def from_json(cls, data: dict) -> "Product":
        d = data

        price_info = d.get("price", {})
        sale = price_info.get("sale_price_without_tax", {})
        nonsale = price_info.get("non_sale_price_without_tax", {})
        base_price = price_info.get("without_tax", {})

        return cls(
            sku=d.get("sku", ""),
            gtin=d.get("gtin", "") or "",
            mpn=d.get("mpn", "") or "",
            upc=d.get("upc", "") or "",
            weight=d.get("weight", 0.0) or 0.0,
            price=base_price.get("value", 0.0),
            currency=base_price.get("currency", "USD"),
            sale_price=sale.get("value", 0.0),
            non_sale_price=nonsale.get("value", 0.0),
            in_stock=d.get("instock", False),
            out_of_stock_message=d.get("out_of_stock_message", ""),
            purchasing_message=d.get("purchasing_message", ""),
            stock_message=d.get("stock_message", ""),
            purchasable=d.get("purchasable", False),
            out_of_stock_behavior=d.get("out_of_stock_behavior", "")
        )
    
#     @classmethod
#     def from_json(cls, data: dict) -> "Product":
#         d = data
# 
#         price_info = d.get("price", {})
#         sale = price_info.get("sale_price_without_tax", {})
#         nonsale = price_info.get("non_sale_price_without_tax", {})
#         base_price = price_info.get("without_tax", {})
# 
#         return cls(
#             sku=d.get("sku", ""),
#             gtin=d.get("gtin", "") or "",
#             mpn=d.get("mpn", "") or "",
#             upc=d.get("upc", "") or "",
#             weight=d.get("weight", 0.0) or 0.0,
#             price=base_price.get("value", 0.0),
#             currency=base_price.get("currency", "USD"),
#             sale_price=sale.get("value", 0.0),
#             non_sale_price=nonsale.get("value", 0.0),
#             in_stock=d.get("instock", False),
#             out_of_stock_message=d.get("out_of_stock_message", ""),
#             purchasing_message=d.get("purchasing_message", ""),
#             stock_message=d.get("stock_message", ""),
#             purchasable=d.get("purchasable", False),
#             out_of_stock_behavior=d.get("out_of_stock_behavior", "")
#         )