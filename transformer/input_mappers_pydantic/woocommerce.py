from pydantic import BaseModel


class WooCommerceProduct(BaseModel):
    pass

    @staticmethod
    def from_json(data: dict):
        pass