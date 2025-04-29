import pandas as pd
import json


class TransformerHandler:
    def __init__(self, vendor: str, used_extraction_strategy: str) -> None:
        self.vendor = vendor.lower()
        self.used_extraction_strategy = used_extraction_strategy

    def perform_transformation(self):
        self.transform()
        self.write_to_file()

    def transform(self, data):
        if self.vendor == "shopify":
            if self.used_extraction_strategy == "ShopifyAPIStrategy":
                """Can be used as-is, does not need transformation"""

                with open("result_files/transformation_results/result_transformed.json", "w") as file:
                    json.dump(data, file, indent=4)

                return pd.read_json(data)

            elif self.used_extraction_strategy == "SitemapSingleProductStrategy":
                with open("result_files/transformation_results/result_transformed.json", "w") as file:
                    json.dump(data, file, indent=4)

                return pd.DataFrame(data)
            
            else:
                raise ValueError(
                    "Transformation Strategy not Supported!! / No transformation strategy was defined"
                )

    def write_to_file(self):
        pass
