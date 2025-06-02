import curl_cffi.requests
import xml.etree.ElementTree as ET
import re
import logging



class ShopifySitemapSingleProductStrategy:

    NAMESPACES = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    def __init__(self):
        self.session = curl_cffi.requests.Session(
            impersonate="chrome", 
            proxies={
                "http":  "http://localhost:8888",
                "https": "http://localhost:8888",
            }
        )
        self.logger = logging.getLogger(self.__class__.__name__)


    def extract(self, url):

        base_sitemap_url = f"https://{url}/sitemap.xml"

        response = self.session.get(base_sitemap_url)

        if response.status_code != 200:
            self.logger.error(
                "Error al obtener información sobre el sitemap: '%s' (Error %d). Abortando extracción",
                base_sitemap_url,
                response.status_code
            )
            raise Exception(
                f"Error al obtener información sobre el sitemap: {base_sitemap_url} (Error {response.status_code}). Abortando extracción"
            )
        
        
        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as e:
            self.logger.error("Error parseando XML de %s. (Error: %s). Abortando extracción", base_sitemap_url, e)
            raise Exception(f"Error parseando XML de {base_sitemap_url}. (Error: {e}) Abortando extracción")


        sitemap_urls = []

        for sitemap in root.findall("ns:sitemap", self.NAMESPACES):
            loc_element = sitemap.find("ns:loc", self.NAMESPACES)
            if loc_element is not None:
                loc_text = loc_element.text
                if re.match(rf"^https://{re.escape(url)}/sitemap_products.*\.xml.*", loc_text):
                    sitemap_urls.append(loc_element)


        product_urls = self._get_product_urls(url, sitemap_urls)
        self.logger.info("Se han obtenido %d URLs de producto", len(product_urls))
        product_json_urls = [f"{prod_url}.json" for prod_url in product_urls]

        product_json_contents: list[dict] = []

        for product_url in product_json_urls:
            data, extraction_strategy_used = self._extract_product_info(product_url)

            if data:
                product_json_contents.append({
                    "url": product_url[:-5], 
                    "data": data, 
                    "extraction_strategy_used": extraction_strategy_used
                })

        self.logger.info("Se han obtenido datos de un total de %d productos", len(product_json_contents))
        return product_json_contents
    

    def _extract_product_info(self, url):

        def from_json_product_endpoint():
            response = self.session.get(url)

            if response.status_code != 200:
                self.logger.error("No se han podido obtener datos JSON de la URL '%s'. (Error: %d)", url, response.status_code)
                return None, "from_json_product_endpoint"
            
            json_response = [response.json().get("product")]

            products = []

            for item in json_response:
                products.append(item)

            return products, "from_json_product_endpoint"


    
        strategies = [from_json_product_endpoint]

        for strategy in strategies:
            self.logger.info(
                "[%s]. Para extraer los datos de Producto, se está utilizando la estrategia: '%s'",
                self.__class__.__name__,
                strategy.__name__,
            )

            try:
                data, extraction_strategy_used = strategy()
                if isinstance(data, (dict, list)):
                    return data, extraction_strategy_used
            except Exception as e:
                self.logger.error("Falló la estrategia '%s' en obtener datos de Producto. Error: '%s'", strategy.__name__, e)
                continue
        
        # Si falla, no devolver datos
        return None, ""


    def _get_product_urls(self, base_url, sitemap_urls):
        product_urls = []
        pattern = rf"^https://{re.escape(base_url)}/products/.+"

        for sitemap_url in sitemap_urls:
            response = self.session.get(sitemap_url.text)
            if response.status_code != 200:
                print(f"Failed to fetch sitemap: {sitemap_url}")
                continue

            sitemap_root = ET.fromstring(response.text)
            urls_in_sitemap = [
                url_tag.find('ns:loc', self.NAMESPACES).text
                for url_tag in sitemap_root.findall('ns:url', self.NAMESPACES)
                if re.match(pattern, url_tag.find('ns:loc', self.NAMESPACES).text)
            ]

            product_urls.extend(urls_in_sitemap)

        return product_urls
    

    def _fetch_json_content(self, json_url):
        response = self.session.get(json_url)
        if response.status_code != 200:
            print(f"Error fetching JSON data: {json_url}")
            return None
        return response.json()