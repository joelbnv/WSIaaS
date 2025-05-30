import curl_cffi.requests
import xml.etree.ElementTree as ET
import re
from bs4 import BeautifulSoup
import demjson3
import json


class WixSitemapSingleProductStrategy:
    """
    Steps:

    1. Locate sitemap (for now, we'll do it statically, later we can try figuring out the sitemap URL through robots.txt)
    2. Go to Sitemap URL and then find the specific Sitemap section for products
    3. Get a list of links of all products.
    4. Open a full browser and load each link, then once loaded parse the value of the variable "BCData" (var BCData) from the source (probably no need to use a full browser, it likely is enough with a curl.cffi.Session.get request).
    5. Given the IDs of the product variation, target the API endpoint to get the details of each product variation.
    """

    """
    Después de la extracción de datos, independientemente de las "strategies", deben devolverse un iterable
    que incluya un objeto de producto "Pydantic Model", como "BigCommerceProductVariant".
    """

    NAMESPACES = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    def __init__(self):
        self.session = curl_cffi.requests.Session(impersonate="chrome")

    def extract(self, url):
        base_sitemap_url = f"https://{url}/xmlsitemap.php"

        response = self.session.get(base_sitemap_url)

        if response.status_code != 200:
            raise Exception(
                f"Error al obtener información sobre el sitemap: {base_sitemap_url}"
            )

        root = ET.fromstring(response.text)

        sitemap_urls: set[str] = {
            loc.text
            for sitemap in root.findall(".//{*}sitemap")
            if (loc := sitemap.find("{*}loc")) is not None
            and loc.text.startswith("https://bearpaw.com/xmlsitemap.php?type=products")
        }

        print(f"Número total de URLs de Sitemap asociadas a productos encontradas: {len(sitemap_urls)}")

        product_urls = self._get_product_urls(url, sitemap_urls)

        print(f"Número total de URLs de producto encontradas: {len(product_urls)}")

        # product_ids: set = {self._get_product_id(product) for product in product_urls}
        product_url_id_dict: dict[str, int] = {product_url: self._get_product_id(product_url) for product_url in product_urls}

        product_json_contents: dict[str, dict] = {
            url: self.session.post(
                self.API_ENDPOINT_GET_PRODUCT_ATTRIBUTES.format(id),
                headers={"Content-Type": "application/json"},
                data=json.dumps({"product_id": id}),
            ).json()
            for url, id in product_url_id_dict.items()
        }

        # Deberíamos guardar otro diccionario con la equivalencia de la URL de producto 
        # y el "product_id" correspondiente


        print(f"Número total de ítems de producto recuperados: {len(product_json_contents)}")

        # Sería pertinente guardar un diccionario con la URL del producto y los datos extraídos

        return product_json_contents
    


    def _get_product_id(self, url: str) -> str | None:
        html = self.session.get(url).text
        soup = BeautifulSoup(html, "html.parser")

        # Find script tags
        script_tags = soup.find_all("script")

        # Look for variable "var item" using RegEx
        pattern = re.compile(r"var item\s*=\s*(\{.*?\})\s*;", re.DOTALL)

        # We'll try to correct the "missing reference" later
        item_data = None
        for script in script_tags:
            if script.string:  # skip if the script tag is empty or external
                match = pattern.search(script.string)
                if match:
                    item_data = match.group(1)
                    break

        js_var_content = demjson3.decode(item_data)

        # Error handling might be missing
        parsed_product_id: str | None = js_var_content.get("ProductID")

        if not parsed_product_id:
            raise Exception("No se ha encontrado un ID de producto para el producto con enlace ...")
        
        return parsed_product_id

    def _get_product_urls(self, sitemap_urls: set[str]) -> set[str]:
        product_urls = set()

        # There may be more than 1 page of product URLs (if there are a lot of products)
        for sitemap_url in sitemap_urls:
            response = self.session.get(sitemap_url.text)
            if response.status_code != 200:
                print(f"Failed to fetch sitemap: {sitemap_url}")
                continue

            sitemap_root = ET.fromstring(response.text)
            urls_in_sitemap = {
                loc.text
                for loc in sitemap_root.findall(".//ns:loc", namespaces=self.NAMESPACES)
                if loc.text
            }

            product_urls.add(urls_in_sitemap)

        return product_urls

