import requests
import time


class ShopifyAPIStategy:
    def extract(self, base_url: str) -> list[dict]:
        "Extracts information from Shopify via a hidden /products.json endpoint"

        page = 1
        all_products = []

        while True:
            url = f"https://{base_url}/products.json?limit=250&page={page}"
            response = requests.get(url)

            if response.status_code != 200:
                raise Exception(f"Error {response.status_code} al obtener datos desde endpoint /products.json")
            
            data = response.json()
            products = data.get("products", [])

            if not products:
                break

            all_products.extend(products)
            print(f"Se han obtenido {len(products)} de la página {page}")
            page += 1


            time.sleep(1)


        return all_products