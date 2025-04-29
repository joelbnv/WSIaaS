Feature : Extracción de datos según plataforma
    Como desarrollador del backend
    Quiero extraer datos de e-commerce según plataforma y formato
    Para obtener datos brutos para transformarlos luego

    Scenario: Extraer datos desde Shopify desde la API REST (Legacy)
        Given una URL válida de la tienda Shopify en cuestión
        When ejecuto una extracción usando la estrategia "shopify_rest_extract_all_products"
        Then recibo datos válidos de producto en formato JSON
    
    Scenario: Extraer datos desde Shopify desde las páginas de producto (parte "ld+json" del documento HTML del producto)
        Given una URL válida de la tienda Shopify en cuestión
        When la estrategia "shopify_rest_extract_all_products" no funciona por cualquier motivo y, tras ello, ejecuto una extracción usando la estrategia "shopify_ld_json_extract_product_info"
        Then recibo datos válidos de producto en formato JSON

    Scenario: Extraer datos desde BigCommerce desde las páginas de producto (replicación de llamada a API REST)
        Given una URL válida de la tienda BigCommerce en cuestión
        When ejecuto la estrategia "bigcommerce_rest_extract_single_product_info"
        Then recibo datos válidos de producto en formato JSON (nota: si de replica la petición desde el navegador, funciona. Ejemplo: https://bearpaw.projectahost.com/api/productoptions/7850)