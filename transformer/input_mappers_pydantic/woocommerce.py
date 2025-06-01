from pydantic import BaseModel, ConfigDict
import html


class WooCommerceProduct(BaseModel):
    product_id: str
    product_name: str
    description: str
    rating: str
    review_count: int
    image_link: str
    availability: str
    price: float
    price_currency: str
    sku: str
    product_url: str
    brand_name: str



    model_config = ConfigDict(frozen=True)

    @classmethod
    def from_jsonld(cls, data: dict):
        return cls(
            product_id="",
            product_name=data.get("name", ""),
            description=data.get("description", ""),
            rating=data.get("", ""),
            review_count=data.get("aggregateRating", {}).get("reviewCount"),
            image_link=data.get("image")[0] if data.get("image") else "",
            availability=data.get("offers", {}).get("availability").split("/")[-1],
            price=data.get("offers", {}).get("price"),
            price_currency=data.get("offers", {}).get("priceCurrency"),
            sku=data.get("offers", {}).get("sku"),
            product_url=data.get("offers", {}).get("url"),
            brand_name=data.get("brand", {}).get("name")
        )

    @classmethod
    def from_pysoptions_var(cls, data: dict):
        return cls(
            product_id=(
                data.get("staticEvents", {})
                .get("facebook", {})
                .get("woo_view_content", {})
                [0]
                .get("params", {})
                .get("post_id", "")
            ),
            product_name=(
                data.get("staticEvents", {})
                .get("facebook", {})
                .get("woo_view_content", {})
                [0]
                .get("params", {})
                .get("page_title", "")
            ),
            description="",
            rating="",
            review_count=0,
            image_link="",
            availability="",
            price=(
                data.get("staticEvents", {})
                .get("facebook", {})
                .get("woo_view_content", {})
                [0]
                .get("params", {})
                .get("product_price", "")
            ),
            price_currency="",
            sku="",
            product_url=html.unescape(
                data.get("staticEvents", {})
                .get("facebook", {})
                .get("woo_view_content", [])
                [0]
                .get("params", {})
                .get("event_url", "")
            ),
            brand_name="",
        )