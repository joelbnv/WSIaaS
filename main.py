
import argparse
from scraper.extraction_handler import ExtractionHandler
from transformer.transformer_handler import TransformerHandler
from loader.loader_handler import LoaderHandler

def parse_args():
    parser = argparse.ArgumentParser(description="Web Scraping ETL por Vendor")
    parser.add_argument("--url", required=True, help="URL del la tienda a scrapear (sin https://)", type=str)
    parser.add_argument("--vendor", required=True, choices=["shopify", "prestashop", "bigcommerce"], help="Vendor (plataforma) a scrapear", type=str)
    parser.add_argument("--output", default="extraction_results/result.json", help="Archivo de salida JSON")

    # Database handling
    parser.add_argument("--destination_format", default="csv", choices=["csv", "json", "excel", "sql"], help="Formato de destino")
    parser.add_argument("--db_type", default=None, choices=["sqlite", "mysql", "postgresql"], help="Tipo de base de datos")
    parser.add_argument("--db_config", default=None, help="JSON con configuración de base de datos")

    return parser.parse_args()


def main():
    args = parse_args()

    handler = ExtractionHandler(vendor=args.vendor)
    raw_data, used_strategy_name = handler.extract(args.url)

    # Write extraction to JSON file (only valid for Shopify API Endpoint Extractor, for now)
    handler.dump(raw_data, used_strategy_name)

    transformer = TransformerHandler(args.vendor, used_strategy_name)
    df = transformer.transform(raw_data)

    loader = LoaderHandler(vendor=args.vendor, data=df, destination_format="csv")
    loader.load_data_to_destination()

    print("Proceso de ETL completado. Resultados guardados en loading_results/")


if __name__ == "__main__":
    main()
