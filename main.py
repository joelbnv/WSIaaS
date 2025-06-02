import argparse
from pathlib import Path

from scraper.extraction_handler import ExtractionHandler
from scraper.logging_config import configure_logging
from transformer.transformer_handler import Product, TransformerHandler
from loader.loader_handler import LoaderHandler
from typing import Iterable
import logging


logger = logging.getLogger("MAIN.PY")

def parse_args():
    parser = argparse.ArgumentParser(description="Web Scraping ETL por Vendor")
    parser.add_argument(
        "--url",
        required=True,
        help="URL del la tienda a scrapear (sin https://)",
        type=str,
    )
    parser.add_argument(
        "--vendor",
        required=True,
        choices=["shopify", "prestashop", "bigcommerce", "woocommerce", "wix"],
        help="Vendor (plataforma) a scrapear",
        type=str,
    )
    parser.add_argument(
        "--output",
        default="extraction_results/result.json",
        help="Archivo de salida JSON",
    )

    parser.add_argument(
        "--destination-path",
        default="result_files/loading_results",
        help="Carpeta donde se guardara el/los archivos destino",
        type=Path,
    )

    # Database handling
    parser.add_argument(
        "--destination-format",
        default="csv",
        choices=["csv", "jsonl", "excel", "parquet", "sqlite", "mysql", "postgres"],
        help="Formato de destino",
    )
    parser.add_argument(
        "--db-type",
        default=None,
        choices=["sqlite", "mysql", "postgresql"],
        help="Tipo de base de datos",
    )
    parser.add_argument(
        "--db-config",
        default=None,
        help="JSON con configuración de base de datos",
        type=str, # Will be later loaded as a dict using json.loads()
    )

    parser.add_argument(
        "--db-path", default=None, help="Ruta del archivo de BBDD sqlite", type=Path
    )

    args = parser.parse_args()

    # Validaciones de dominio
    file_formats = {"csv", "jsonl", "excel", "parquet"}

    if args.destination_format in file_formats and not args.destination_path:
        parser.error(
            f"Se requiere especificar '--destination-path' is cuando 'destination_format' es {file_formats}"
        )

    if args.destination_format == "sqlite" and not args.db_path:
        parser.error(
            "Se requiere especificar '--db_path' cuando 'destination_format' is sqlite"
        )

    if args.destination_format in {"mysql", "postgres"} and not args.db_config:
        parser.error(
            "Se requiere especificar '--db_config' cuando 'destination_format' es 'mysql' o 'postgres'"
        )

    return args


def main():
    configure_logging("INFO")
    logging.info("==== INICIO DEL PROGRAMA ETL ====")

    args = parse_args()

    try:
        handler = ExtractionHandler(vendor=args.vendor)
        raw_products, used_strategy_name = handler.extract(args.url)

        transformer = TransformerHandler(args.vendor, used_strategy_name)

        iterable_pydantic_models: Iterable[Product] = transformer.transform(
            raw_products=raw_products
        )

        # transformer.write_to_file()

        loader = LoaderHandler(
            vendor=args.vendor,
            data=iterable_pydantic_models,
            destination_path=args.destination_path,
            destination_format=args.destination_format,
            db_config=args.db_config,
            db_path=args.db_path,
        )
        loader.load()

        logger.info(
            "Proceso de ETL completado. Resultados guardados en '%s'", args.destination_path
        )

    except Exception as e:
        logger.error("Error en la ejecución de la ETL: '%s'", e)
        logger.error("Ejecución abortada")


if __name__ == "__main__":
    main()
