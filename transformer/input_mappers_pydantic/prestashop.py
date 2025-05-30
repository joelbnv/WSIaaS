from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import date


class PrestashopProduct(BaseModel):
    name: str
    description: str
    category: str
    sku: str
    mpn: str
    brand: str
    price: float
    currency: str
    url: HttpUrl
    main_image: Optional[HttpUrl]
    availability: str
    seller: str
    price_valid_until: Optional[date]

    @classmethod
    def from_jsonld(cls, data: dict) -> "PrestashopProduct":
        offers = data.get("offers", {})
        brand = data.get("brand", {})

        # Handle primary image (from top-level 'image') and additional from offers
        main_image = data.get("image", None)

        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            category=data.get("category", ""),
            sku=data.get("sku", ""),
            mpn=data.get("mpn", ""),
            brand=brand.get("name", ""),
            price=float(offers.get("price", 0)),
            currency=offers.get("priceCurrency", "EUR"),
            url=offers.get("url", ""),
            main_image=main_image,
            availability=offers.get("availability", "").split("/")[-1],  # e.g. "InStock"
            seller=offers.get("seller", {}).get("name", ""),
            price_valid_until=offers.get("priceValidUntil", None)
        )
