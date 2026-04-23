"""
Модуль для создания базы данных и таблиц PostgreSQL.
"""

import psycopg2

from src.utils.config import Config


class DBCreator:
    """Класс для создания базы данных и таблиц."""
    def __init__(self):
        self.conn = None
        self.cur = None

    def create_database(self) -> None:
        """Создаёт базу данных, если её нет."""
        try:
            # Подключаемся к стандартной БД postgres
            conn_admin = psycopg2.connect(
                dbname="postgres",
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                host=Config.DB_HOST,
                port=Config.DB_PORT,
            )
            conn_admin.autocommit = True
            cur_admin = conn_admin.cursor()

            # Проверяем, существует ли база
            cur_admin.execute(
                f"SELECT 1 FROM pg_database WHERE datname = '{Config.DB_NAME}'"
            )
            exists = cur_admin.fetchone()

            if not exists:
                cur_admin.execute(f"CREATE DATABASE {Config.DB_NAME}")
                print(f"  База данных '{Config.DB_NAME}' создана")
            else:
                print(f"  База данных '{Config.DB_NAME}' уже существует")

            cur_admin.close()
            conn_admin.close()
        except Exception as e:
            print(f"  Ошибка при создании БД: {e}")

    def create_tables(self) -> None:
        """Создаёт таблицы."""
        try:
            self.conn = psycopg2.connect(
                dbname=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                host=Config.DB_HOST,
                port=Config.DB_PORT,
            )
            self.cur = self.conn.cursor()

            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    url TEXT,
                    description TEXT
                )
            """)

            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS vacancies (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
                    name VARCHAR(255) NOT NULL,
                    url TEXT,
                    salary_from INTEGER,
                    salary_to INTEGER,
                    salary_currency VARCHAR(10)
                )
            """)

            self.conn.commit()
            print("  Таблицы созданы")
        except Exception as e:
            print(f"  Ошибка при создании таблиц: {e}")

    def close(self) -> None:
        """Закрывает соединение с БД."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
