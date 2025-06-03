# 🛠️ Web Scraping Intelligence as a Service - Scraper Backend TFG - ETL para tiendas eCommerce

Este proyecto realiza un proceso ETL (Extracción, Transformación y Carga) para diferentes plataformas de tiendas en línea como **Shopify**, **PrestaShop**, **BigCommerce**, **WooCommerce** y **Wix**. Usa contenedores Docker para facilitar la ejecución y asegurar la portabilidad del entorno

## 🚀 Requisitos

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Acceso a Internet (para el scraping)

---

## 🐳 Construcción de la imagen

Antes de ejecutar cualquier comando, asegúrate de construir las imágenes de Docker:

```bash
docker compose build
```

## Arranque de servicios de base de datos y proxy

Si deseas levantar los servicios auxiliares (MySQL, PostgreSQL y el proxy TinyProxy), ejecuta:

```bash
docker compose up -d mysql postgres tinyproxy
```

Puedes detenerlos con:

```bash
docker compose down
```

# ⚙️ Ejecución del proceso ETL

## Salida en formato CSV (recomendado para pruebas rápidas):

```bash
docker compose run --rm app \
  --url tirachinas.shop \
  --vendor shopify \
  --destination-format csv \
  --destination-path result_files/output.csv
```

## Formato SQLite

```bash
docker compose run --rm app \
  --url tirachinas.shop \
  --vendor shopify \
  --destination-format sqlite \
  --db-path sqlite_dbs/mi_etl.db
```

## Formato MySQL

```bash
docker compose run --rm app \
  --url tirachinas.shop \
  --vendor shopify \
  --destination-format mysql \
  --db-config '{"host": "mysql", "port": 3306, "user": "root", "password": "root", "database": "etl"}'

```

## Formato PostgreSQL

```bash
docker compose run --rm app \
  --url tirachinas.shop \
  --vendor shopify \
  --destination-format postgres \
  --db-config '{"host": "postgres", "port": 5432, "user": "postgres", "password": "postgres", "database": "etl"}'
```


# 🧪 Argumentos disponibles

| Argumento               | Obligatorio | Valores posibles                                                                                      | Descripción                                                                                          |
|-------------------------|-------------|--------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| `--url`                 | ✅ Sí        | Cadena (sin `https://`)                                                                               | Dominio de la tienda a scrapear (ejemplo: `tirachinas.shop`)                                       |
| `--vendor`              | ✅ Sí        | `shopify`, `prestashop`, `bigcommerce`, `woocommerce`, `wix`                                          | Plataforma (vendor) de la tienda                                                                    |
| `--destination-path`    | ❌ No        | Carpeta o archivo                                                                                      | Carpeta o archivo donde se guardarán los resultados transformados y cargados                        |
| `--destination-format`  | ❌ No        | `csv`, `jsonl`, `excel`, `parquet`, `sqlite`, `mysql`, `postgres`                                     | Formato de salida para los datos cargados (por defecto: `csv`)                                      |
| `--db-type`             | ❌ No        | `sqlite`, `mysql`, `postgresql`                                                                        | Tipo de base de datos (opcional, puede omitirse si se define `--destination-format`)                |
| `--db-config`           | ❌ Sí*       | JSON en string (ej: `{"host": "mysql", "port": 3306, "user": "...", ...}`)                            | Requerido si el destino es MySQL o PostgreSQL                                                        |
| `--db-path`             | ❌ Sí*       | Ruta a archivo `.db`                                                                                   | Requerido si el destino es SQLite                                                                    |


- Los argumentos marcados con ❌ Sí* son sobligatorios dependiendo del valor de `--destination-format`.


# 🔍 Debugging

Para entrar al contenedor y ejecutar comandos manualmente:

```bash
docker compose run --rm --entrypoint bash app
```

Desde allí, puedes ejecutar el script manualmente:

```bash
python main.py --url tirachinas.shop --vendor shopify --destination-format csv --destination-path result_files
```

# 📂 Estructura de carpetas

- result_files/: Archivos generados por el proceso ETL.
- sqlite_dbs/: Archivos .db si usas SQLite.
- scraper/, transformer/, loader/: Módulos de la pipeline ETL


# Notas

- El contenedor tinyproxy se utiliza para anonimizar el scraping vía proxy (puerto 8888).
- El parámetro PROXY_HOST se configura automáticamente en el entorno de Docker Compose (tinyproxy).
- Para pruebas en local sin Docker, puedes ejecutar el script con el entorno virtual:

    Si se usa un entorno virtual en Windows, una vez satisfechas las dependencias especificadas en **requirements.txt**

    - Crear entorno virtual (desde la carpeta del proyecto):

    ```bash
    python3 -m venv .venv
    ```

    - Activar entorno virtual (desde la carpeta del proyecto):

    ```bash
    & .\.venv\Scripts\activate.ps1
    ```
    
    - Statisfacer dependencias:

    ```bash
    pip install -r requirements.txt
    ```

    - Ejecutar proceso ETL:

    ```bash
    python main.py --url tirachinas.shop --vendor shopify --destination-format csv --destination-path result_files
    ```

# Licencia

Este proyecto se desarrolla como parte del Trabajo de Fin de Grado.