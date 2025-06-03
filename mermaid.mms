classDiagram

%% === Interface: Product Extraction Strategy ===
class ProductStrategy {
  <<interface>>
  +extract()
}

%% === Strategy Implementations ===
class BigCommerceSitemapSingleProductStrategy {
  +extract()
}
class ShopifyAPIBulkStategy {
  +extract()
}
class ShopifySitemapSingleProductStrategy {
  +extract()
}
class WixSitemapSingleProductStrategy {
  +extract()
}
class WooCommerceSitemapSingleProductStrategy {
  +extract()
}

ProductStrategy <|.. BigCommerceSitemapSingleProductStrategy
ProductStrategy <|.. ShopifyAPIBulkStategy
ProductStrategy <|.. ShopifySitemapSingleProductStrategy
ProductStrategy <|.. WixSitemapSingleProductStrategy
ProductStrategy <|.. WooCommerceSitemapSingleProductStrategy

%% === Informal Interface for Validated Product ===
class PydanticValidatedProduct {
  <<interface>>
  +from_source_n() $
}

%% === Concrete Product Implementations ===
class BigCommerceProduct {
  +from_json() $
}
class PrestashopProduct {
  +from_jsonld() $
}
class ShopifyProductVariant {
  +from_json() $
}
class WixProduct {
  +from_jsonld() $
}
class WooCommerceProduct {
  +from_jsonld() $
  +from_pysoptions_var() $
}

PydanticValidatedProduct <|.. BigCommerceProduct
PydanticValidatedProduct <|.. PrestashopProduct
PydanticValidatedProduct <|.. ShopifyProductVariant
PydanticValidatedProduct <|.. WixProduct
PydanticValidatedProduct <|.. WooCommerceProduct

%% === Handlers ===
class ExtractionHandler {
  +vendor: str
  +strategy_chain
  +logger
  +extract()
}
class TransformerHandler {
  +vendor: str
  +used_extraction_strategy: str
  +transform()
}
class LoaderHandler {
  +data: Iterable[Product]
  +destination_format: str
  +destination_path: Path
  +vendor: str
  +db_config: dict | str | None
  +db_path: str | None
  +load()
}

%% === Relationships ===
ExtractionHandler *-- ProductStrategy : uses
LoaderHandler "1" o-- "n" PydanticValidatedProduct : transforms →


ExtractionHandler --> TransformerHandler : error →
TransformerHandler --> LoaderHandler : error →
TransformerHandler --> PydanticValidatedProduct

