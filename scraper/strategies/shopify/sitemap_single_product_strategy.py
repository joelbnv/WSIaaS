import curl_cffi.requests
import xml.etree.ElementTree as ET
import re
import requests

class SitemapSingleProductStrategy:

    NAMESPACES = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    def __init__(self):
        self.session = curl_cffi.requests.Session(impersonate="chrome")


    def extract(self, url):

        base_sitemap_url = f"https://{url}/sitemap.xml"

        response = self.session.get(base_sitemap_url)

        if response.status_code != 200:
            raise Exception(f"Error al obtener información sobre el sitemap: {base_sitemap_url}")
        
        
        root = ET.fromstring(response.text)
        
        sitemap_urls = [
            sitemap.find("sm:loc", self.NAMESPACES)
            for sitemap in root.findall("sm:sitemap", self.NAMESPACES)
            if re.match(rf"^https://{re.escape(url)}/sitemap_products.*\.xml.*", sitemap.find('sm:loc', self.NAMESPACES).text)
        ]

        product_urls = self._get_product_urls(url, sitemap_urls)
        
        product_json_urls = [f"{prod_url}.json" for prod_url in product_urls]
        product_json_contents = [self._fetch_json_content(json_url).get("product") for json_url in product_json_urls]

        return product_json_contents
    


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
                url_tag.find('sm:loc', self.NAMESPACES).text
                for url_tag in sitemap_root.findall('sm:url', self.NAMESPACES)
                if re.match(pattern, url_tag.find('sm:loc', self.NAMESPACES).text)
            ]

            product_urls.extend(urls_in_sitemap)

        return product_urls
    

    def _fetch_json_content(self, json_url):
        response = self.session.get(json_url)
        if response.status_code != 200:
            print(f"Error fetching JSON data: {json_url}")
            return None
        return response.json()