import curl_cffi.requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
import logging
import html


class WooCommerceSitemapSingleProductStrategy:

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
            self.logger.error("Error al obtener sitemap: %s (status '%s')", base_sitemap_url, response.status_code)
            raise Exception(f"Error al obtener sitemap: {base_sitemap_url} (status {response.status_code})")

        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as e:
            self.logger.error("Error parseando XML de %s: %s", base_sitemap_url, e)
            raise Exception(f"Error parseando XML de {base_sitemap_url}: {e}")


        sitemap_urls: set[str] = {
            loc.text
            for loc in root.findall('.//ns:loc', self.NAMESPACES)
            if "product" in loc.text 
        }

        self.logger.info("WooCommerceSitemap: Encontradas %d posibles URLs de Sitemap de Producto", len(sitemap_urls))
        
        product_urls = self._get_product_urls(sitemap_urls)
        self.logger.info("Número total de URLs de producto encontradas: %s", len(product_urls))


        # We exclude the records where no response was found
        product_json_contents: list[dict] = []

        for index, product_url in enumerate(product_urls, start=1):
            self.logger.info("Solicitando JSON para URL de producto: '%s' (%d de %d)", product_url, index, len(product_urls))
            response = self.session.get(product_url)

            if response.status_code != 200:
                self.logger.error("No se pudo recuperar el código fuente para extraer los datos de la URL (%s)", product_url)
                continue

            # Cada producto puede tener más de un Variant, y este se debe almacenar
            data, extraction_strategy_used = self._extract_product_info(response.text)

            # If there is a non-empty response, url and JSON object to dictionary
            if data:
                product_json_contents.append({
                    "url": product_url, 
                    "data": data, 
                    "extraction_strategy_used": extraction_strategy_used
                })

            
        self.logger.info("Número total de ítems de producto recuperados: %d", len(product_json_contents))

        return product_json_contents




    def _extract_product_info(self, html_source: str):

        soup = BeautifulSoup(html_source, "html.parser")

        # Estrategia 1
        def from_pysoptions_var():

            script = soup.find("script", {"id": "pys-js-extra"})

            if not script:
                raise Exception("No se encontró un script con id='pys-js-extra'")
            
            script_content = script.text

            unescaped_content = html.unescape(script_content)

            # Extracción de la estructura JSON en base a la variable JS
            prefix = "var pysOptions = "
            if not unescaped_content.strip().startswith(prefix):
                raise ValueError("Unexpected script content format")

            # Seleccionamos a partir del prefijo
            json_part = unescaped_content.strip()[len(prefix):]

            # Quitamos el punto y coma si existe
            if json_part.endswith(";"):
                json_part = json_part[:-1]

            pys_options = json.loads(json_part)
            return pys_options, "from_pysoptions_var"
        

        # Estrategia 2
        def from_ld_json():

            script = soup.find("script", {"type": "application/ld+json", "class": "y-rich-snippet-script"})

            if not script:
                raise Exception("No se encontró un script con id=application/ld+json y class=y-rich-snippet-script")
            
            script_content = script.text.strip()
            unescaped_content = html.unescape(script_content)
            
            json_dict = json.loads(unescaped_content)
            self.logger.info("Se obtuvo información de producto CORRECTAMENTE con la estrategia '%s'", strategy.__name__)
            return json_dict, "from_ld_json"


        # List of strategies
        strategies = [from_ld_json, from_pysoptions_var]

        for strategy in strategies:
            self.logger.info(
                "[%s]. Para extraer los datos de Producto, se está utilizando la estrategia: '%s'",
                self.__class__.__name__,
                strategy.__name__,
            )

            try:
                data, extraction_strategy_used = strategy()
                if isinstance(data, dict):
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

            urls_in_sitemap = {
                loc.text
                for loc in root.findall(".//ns:loc", namespaces=self.NAMESPACES)
                if loc.text
            }

            product_urls.update(urls_in_sitemap)

        return product_urls