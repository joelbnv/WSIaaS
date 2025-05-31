import mysql.connector
import psycopg2
import sqlite3
from mysql.connector import Error as MySQLError
from psycopg2 import OperationalError as PostgresError


class MySQLDB:
    def __init__(self, conn_params: dict):

        host = conn_params.get("host", "")
        user = conn_params.get("user", "")
        password = conn_params.get("password", "")
        dbname = conn_params.get("dbname", "")
        port = int(conn_params.get("port"))

        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": dbname,
            "port": port
        }
        self.conn = None
        self.cursor = None

    def __enter__(self):
        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor()
            return self.conn, self.cursor
        except MySQLError as e:
            print(f"MySQL Connection Error: {e}")
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


class PostgreSQLDB:
    def __init__(self, conn_params: dict):

        host = conn_params.get("host", "")
        user = conn_params.get("user", "")
        password = conn_params.get("password", "")
        dbname = conn_params.get("dbname", "")
        port = int(conn_params.get("port"))

        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "dbname": dbname,
            "port": port,
        }
        self.conn = None
        self.cursor = None

    def __enter__(self):
        try:
            self.conn = psycopg2.connect(**self.config)
            self.cursor = self.conn.cursor()
            return self.conn, self.cursor
        except PostgresError as e:
            print(f"PostgreSQL Connection Error: {e}")
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


class SQLiteDB:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None
        self.cursor = None

    def __enter__(self):
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.cursor = self.conn.cursor()
            return self.conn, self.cursor
        except sqlite3.Error as e:
            print(f"SQLite Connection Error: {e}")
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
