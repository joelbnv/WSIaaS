import ast
from pathlib import Path
from transformer.transformer_handler import Product
from typing import Iterable

from loader.loader_writers import (
    write_batch_csv,
    write_batch_excel,
    write_batch_jsonl,
    write_batch_parquet,
    write_batch_mysql,
    write_batch_sqlite,
    write_batch_postgres,
)


class LoaderHandler:
    def __init__(
        self,
        data: Iterable[Product],
        destination_format: str,
        destination_path: Path,
        vendor: str,
        db_config: dict | str | None = None,
        db_path: str | None = None,
    ):
        self.data = data
        self.destination_format = destination_format
        self.destination_path = destination_path
        self.vendor = vendor
        self.db_config = (
            # We'll use ast.literal_eval() to be able to import dict-like string that uses single-quote
            ast.literal_eval(db_config) if isinstance(db_config, str) else db_config
            # json.loads(db_config) if isinstance(db_config, str) else db_config
        )
        self.db_path = db_path

    def load(self) -> None:
        if self.destination_format == "csv":
            write_batch_csv(self.data, path=Path(self.destination_path))

        elif self.destination_format == "jsonl":
            write_batch_jsonl(self.data, path=Path(self.destination_path))

        elif self.destination_format == "excel":
            write_batch_excel(self.data, path=Path(self.destination_path))

        elif self.destination_format == "parquet":
            write_batch_parquet(self.data, path=Path(self.destination_path))

        elif self.destination_format == "sqlite":
            write_batch_sqlite(self.data, table="Products", db_path=self.db_path)

        elif self.destination_format == "mysql":
            write_batch_mysql(self.data, table="Products", conn_params=self.db_config)

        elif self.destination_format == "postgres":
            write_batch_postgres(self.data, table="Products", conn_params=self.db_config)
