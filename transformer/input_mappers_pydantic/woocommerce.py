from pydantic import BaseModel, ConfigDict


class WooCommerceProduct(BaseModel):
    pass

    model_config = ConfigDict(frozen=True)

    @staticmethod
    def from_json(data: dict):
        pass