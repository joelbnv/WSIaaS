from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


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
    def from_json(
        cls, product: dict, variant: dict, image_url: Optional[str] = ""
    ) -> "ShopifyProductVariant":
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
            updated_at=variant.get("updated_at", datetime.utcnow()),
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
        image_url = data.get("image", {}).get("src", "")
        variants = data.get("variants", [])

        validated_list = [
            ShopifyProductVariant.from_json(data, variant, image_url)
            for variant in variants
        ]
        return validated_list

    @staticmethod
    def from_json_bulk_api(payload: dict) -> List[ShopifyProductVariant]:
        all_variants = []
        for product in payload.get("products", []):
            all_variants.extend(ShopifyProduct.from_json(product))
        return all_variants
