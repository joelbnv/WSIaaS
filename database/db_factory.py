from database.databases import SQLiteDB, MySQLDB, PostgreSQLDB

class DatabaseFactory:
    @staticmethod
    def get_database(db_type: str, config: dict):
        db_type = db_type.lower()
        if db_type == "mysql":
            return MySQLDB(**config)
        elif db_type == "postgresql":
            return PostgreSQLDB(**config)
        elif db_type == "sqlite":
            return SQLiteDB(**config)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
