Feature: Transformación de datos extraídos
    Como desarrollador del backend
    Quiero transformar datos brutos a formato tabular estándar
    Para facilitar la carga de los datos

    Scenario: Transformar datos JSON de Shopify a formato estándar
        Given datos extraídos en formato JSON desde Shopify
        When transformo los datos usando el método para Shopify
        Then obtengo un DataFrame válido con columnas estándar

    Scenario: Transformar HTML de BigCommerce a formato estándar
        Given datos extraídos en formato HTML desde BigCommerce
        When transformo los datos usando el método para BigCommerce
        Then obtengo un DataFrame válido con columnas estándar


    Scenario: Transformar HTML de WooCommerce a formato estándar
        Given datos extraídos en formato HTML desde WooCommerce
        When transformo los datos usando el método para WooCommerce
        Then obtengo un DataFrame válido con columnas estándar
