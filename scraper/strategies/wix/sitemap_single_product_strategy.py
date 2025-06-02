import html
import itertools
import logging
import curl_cffi.requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
import os

proxy_host = os.getenv("PROXY_HOST", "localhost")



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

    NAMESPACES = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    def __init__(self):
        self.session = curl_cffi.requests.Session(
            impersonate="chrome", 
            proxies={
                "http":  f"http://{proxy_host}:8888",
                "https": f"http://{proxy_host}:8888",
            }
        )
        self.logger = logging.getLogger(self.__class__.__name__)

    def extract(self, url):
        
        """
        NOTA IMPORTANTE: Para los Sitemap, parece ser que incluso el mismo "vendor" puede
        tener diferentes patrones de SiteMaps y SubSitemaps (nos centramos en este caso
        en los productos).

        Por ello, deberíamos implementar funciones auxiliares que nos permitan hacer un mapping del patrón de 
        SiteMap y SubSitemaps para encontrar los enlaces de producto, que al final es lo que se busca.

        Por el momento está definido de forma estática, pero debería determinarse mediante pruebas de forma
        dinámica en tiempo de ejecución.

        Una forma de empezar el hacer parsing al fichero "robots.txt", y a partir de los diferentes "slug" y
        modelos de SiteMap y SubSitemap generar funciones auxiliares para sacar los enlaces de producto.
        """

        # base_sitemap_url = f"https://{url}/sitemap-index.xml"
        base_sitemap_url = f"https://{url}/sitemap.xml"
        self.logger.info("WixSitemap: Obteniendo sitemap principal: '%s'", base_sitemap_url)

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

        sitemap_urls: set[str] = {
            loc.text
            for loc in root.findall('.//ns:loc', self.NAMESPACES)
            if "products" in loc.text
            # if not "Image" in loc.text
        }

        self.logger.info("WixSitemap: Encontradas %d posibles URLs de Sitemap de Producto", len(sitemap_urls))

        product_urls = self._get_product_urls(sitemap_urls)
        self.logger.info("Número total de URLs de producto encontradas: %s", len(product_urls))


        # Para hacer pruebas, tomamos un slice de 40 enlaces
        product_urls = list(itertools.islice(product_urls, 40))

        # We exclude the records where no response was found
        product_json_contents: list[dict] = []

        for product_url in product_urls:
            self.logger.info("Solicitando JSON para URL de producto: '%s'", product_url)
            response = self.session.get(product_url)

            if response.status_code != 200:
                self.logger.error("No se pudieron extraer los datos de la URL (%s). Error %d", product_url, response.status_code)
                continue
            
            # Cada producto puede tener más de un Variant, y este se debe almacenar
            # data: list[dict] | dict = self._extract_products_from_source_code(response.text, product_url)
            data, extraction_strategy_used = self._extract_product_info(response.text, product_url)

            # If there is a non-empty response, url and JSON object to dictionary
            if data:
                product_json_contents.append({
                    "url": product_url, 
                    "data": data, 
                    "extraction_strategy_used": extraction_strategy_used
                })


        self.logger.info("Número total de ítems de producto recuperados: %d", len(product_json_contents))

        return product_json_contents
        
    

    def _extract_product_info(self, html_source_string: str, product_url: str):
        html_doc = BeautifulSoup(html_source_string, "html.parser")

    
        def from_jsonld():

            ld_json_script = html_doc.find("script", type="application/ld+json")

            if not ld_json_script:
                self.logger.error("No existe un objeto <script type=application/ld+json> en la URL '%s'", product_url)
                return None
            
            unescaped_content = html.unescape(ld_json_script.text)

            try:
                ld_json_list = [json.loads(unescaped_content)]
            except (json.JSONDecodeError, Exception) as e:
                self.logger.error("Error en el parsing del formato JSON+LD a diccionario: %s", e)
                return None

            products = []

            for item in ld_json_list:
                if item.get("@type") == "Product":
                    products.append(item)

            return products, "from_jsonld"
        
        strategies = [from_jsonld]

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




    def _get_product_urls(self, sitemap_urls: set[str]) -> set[str]:
        product_urls = set()

        # There may be more than 1 page of product URLs (if there are a lot of products)
        for sitemap_url in sitemap_urls:
            response = self.session.get(sitemap_url)

            if response.status_code != 200:
                self.logger.error("Error HTTP %s navegado por el sitemap '%s'", response.status_code, sitemap_url)
                continue

            try:
                root = ET.fromstring(response.text)
            except ET.ParseError as e:
                self.logger.error("Error parseando XML de %s: %s", sitemap_url, e)
                raise Exception(f"Error parseando XML de {sitemap_url}: {e}")

            # urls_in_sitemap = {
            #     loc.text
            #     for loc in root.findall(".//ns:loc", namespaces=self.NAMESPACES)
            #     if '/en/' in loc.text
            # }

            urls_in_sitemap = {
                loc.text
                for loc in root.findall(".//ns:loc", namespaces=self.NAMESPACES)
                if loc.text
            }

            product_urls.update(urls_in_sitemap)

        return product_urls

