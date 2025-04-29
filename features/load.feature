Feature: Carga de datos transformados
    Como desarrollador del backend
    Quiero cargar datos tabulares en destinos específicos
    Para persistir y entregar resultados a usuarios

    Scenario: Cargar datos transformados a archivo CSV
        Given datos tabulares transformados en un DataFrame
        When cargo los datos en formato "CSV"
        Then obtengo un archivo CSV válido

    Scenario: Cargar datos transformados a base de datos PostgreSQL
        Given datos tabulares transformados en un DataFrame
        When cargo los datos en base de datos "PostgreSQL"
        Then los datos se guardan correctamente en PostgreSQL
