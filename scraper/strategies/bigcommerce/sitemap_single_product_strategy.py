import curl_cffi.requests
import xml.etree.ElementTree as ET
import re
from bs4 import BeautifulSoup
import demjson3
import json
import itertools
import logging


class BigCommerceSitemapSingleProductStrategy:
    """
    Steps:

    1. Locate sitemap (for now, we'll do it statically, later we can try figuring out the sitemap URL through robots.txt)
    2. Go to Sitemap URL and then find the specific Sitemap section for products
    3. Get a list of links of all products.
    4. Open a full browser and load each link, then once loaded parse the value of the variable "BCData" (var BCData) from the source (probably no need to use a full browser, it likely is enough with a curl.cffi.Session.get request).
    5. Given the IDs of the product variation, target the API endpoint to get the details of each product variation.
    """

    NAMESPACES = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    # GET REQUEST
    # API_ENDPOINT_GET_PRODUCT_OPTIONS: str = (
    #     "https://{bearpaw}.projectahost.com/api/productoptions/{}"
    # )

    # POST REQUEST
    API_ENDPOINT_GET_PRODUCT_ATTRIBUTES: str = (
        "https://{}/remote/v1/product-attributes/{}"
    )

    def __init__(self):
        self.session = curl_cffi.requests.Session(impersonate="chrome")
        self.logger = logging.getLogger(self.__class__.__name__)

    def extract(self, url):
        base_sitemap_url = f"https://{url}/xmlsitemap.php"

        response = self.session.get(base_sitemap_url)

        if response.status_code != 200:
            self.logger.error(
                "Error al obtener información sobre el sitemap: %s. Abortando extracción",
                base_sitemap_url,
            )
            raise Exception(
                f"Error al obtener información sobre el sitemap: {base_sitemap_url}. Abortando extracción"
            )

        root = ET.fromstring(response.text)

        sitemap_urls = set()

        # Patrón para MATCH de URL
        pattern = re.compile(
            rf"^https://(www\.)?{re.escape(url)}/xmlsitemap\.php\?type=products"
        )

        for sitemap in root.findall(".//ns:sitemap", namespaces=self.NAMESPACES):
            loc = sitemap.find("ns:loc", namespaces=self.NAMESPACES)
            if loc is not None and loc.text and pattern.match(loc.text):
                sitemap_urls.add(loc.text)

        print(
            f"Número total de URLs de Sitemap asociadas a productos encontradas: {len(sitemap_urls)}"
        )

        product_urls = self._get_product_urls(sitemap_urls)
        self.logger.info("Se han obtenido %d URLs de producto", len(product_urls))
        # print(f"Número total de URLs de producto encontradas: {len(product_urls)}")

        # Para hacer pruebas, nos quedamos solamente con las primeras 10 URLs
        product_urls = list(itertools.islice(product_urls, 10))

        # product_ids: set = {self._get_product_id(product) for product in product_urls}
        product_url_id_dict: dict[str, int] = {
            product_url: self._get_product_id(product_url)
            for product_url in product_urls
        }

        product_json_contents: list[dict] = []

        for product_url, id in product_url_id_dict.items():
            response = self.session.post(
                self.API_ENDPOINT_GET_PRODUCT_ATTRIBUTES.format(url, id),
                headers={"Content-Type": "application/json"},
                data=json.dumps({"product_id": id}),
            )

            if response.status_code != 200:
                self.logger.error(
                    "Código de Error (%d). La petición a la URL '%s' fallo. Error: '%s'",
                    response.status_code,
                    self.API_ENDPOINT_GET_PRODUCT_ATTRIBUTES.format(url, id),
                    response.text,
                )
                continue

            data = response.json()

            if data:
                product_json_contents.append({"url": product_url, "data": data})

        self.logger.info(
            "Se han obtenido datos de un total de %d productos",
            len(product_json_contents),
        )

        return product_json_contents

    def _get_product_id(self, url: str) -> str | None:
        html = self.session.get(url).text
        soup = BeautifulSoup(html, "html.parser")

        def from_var_item() -> str | None:
            # Find script tags
            script_tags = soup.find_all("script")
            # Look for variable "var item" using RegEx
            pattern = re.compile(r"var item\s*=\s*(\{.*?\})\s*;", re.DOTALL)

            for script in script_tags:
                if script.string:  # skip if the script tag is empty or external
                    match = pattern.search(script.string)
                    if match:
                        item_data = match.group(1)
                        js_var_content = demjson3.decode(item_data)
                        return js_var_content.get("ProductID")
            return None

        def from_data_product_id_attr() -> str | None:
            container = soup.find("div", class_="product-page-container")
            if container and container.has_attr("data-product-id"):
                return container["data-product-id"]
            return None

        # List of strategies to get the id
        strategies = [from_var_item, from_data_product_id_attr]

        for strategy in strategies:
            self.logger.info(
                "[%s]. Para sacar el ID de producto, se está utilizando la estrategia: '%s'",
                self.__class__.__name__,
                strategy.__name__,
            )
            try:
                product_id = strategy()
                if product_id is not None and str(product_id).isdigit():
                    self.logger.info(
                        "Se ha podido extraer el ProductID con la estrategia '%s'",
                        strategy.__name__,
                    )
                    return str(product_id)
            except Exception as e:
                self.logger.error(
                    "Error en la extracció de ID de producto para llamada a API Interna. Error: %s",
                    e,
                )
                continue
        # In any other case, return None
        return None

    def _get_product_urls(self, sitemap_urls: set[str]) -> set[str]:
        product_urls = set()

        # There may be more than 1 page of product URLs (if there are a lot of products)
        for sitemap_url in sitemap_urls:
            response = self.session.get(sitemap_url)
            if response.status_code != 200:
                print(f"Failed to fetch sitemap: {sitemap_url}")
                continue

            sitemap_root = ET.fromstring(response.text)
            urls_in_sitemap = {
                loc.text
                for loc in sitemap_root.findall(".//ns:loc", namespaces=self.NAMESPACES)
                if loc.text
            }

            product_urls.update(urls_in_sitemap)

        return product_urls
