import curl_cffi.requests
import xml.etree.ElementTree as ET
import re
from bs4 import BeautifulSoup
import demjson3
import json


class WooCommerceSitemapSingleProductStrategy:

    NAMESPACES = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    def __init__(self):
        self.session = curl_cffi.requests.Session(impersonate="chrome")

    def extract(self, url):
        base_sitemap_url = f"https://{url}/wp-sitemap.xml"

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