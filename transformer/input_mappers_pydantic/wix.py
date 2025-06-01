from pydantic import BaseModel, ConfigDict


class WixProduct(BaseModel):
    asset_type: str
    sku: str
    product_name: str
    image_url: str
    product_description: str
    gtin13: str
    brand_name: str
    availability: str
    price: float
    price_currency: str

    model_config = ConfigDict(frozen=True)

    @classmethod
    def from_jsonld(cls, data: dict) -> "WixProduct":
        return cls(
            asset_type=data.get("@type", ""),
            sku=data.get("sku", ""),
            product_name=data.get("name", ""),
            image_url=data.get("image", "")[0],
            product_description=data.get("description", ""),
            gtin13=data.get("gtin13", ""),
            brand_name=data.get("brand", {}).get("name", ""),
            availability=data.get("offers", {}).get("availability", "").split("/")[-1],
            price=float(data.get("offers", {}).get("price", 0)),
            price_currency=data.get("offers", {}).get("priceCurrency", ""),
        )
