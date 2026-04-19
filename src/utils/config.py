"""
Конфигурация для подключения к PostgreSQL.
Данные берутся из переменных окружения(.env файл).
"""

import os
from dotenv import load_dotenv

# Заглушаем переменные из .env (если есть)
load_dotenv()

class Config:
     """Настройки подключения к базе данных."""

     DB_NAME = os.getenv("DB_NAME", "hh_vacancies")
     DB_USER = os.getenv("DB_USER", "postgres")
     DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
     DB_HOST = os.getenv("DB_HOST", "localhost")
     DB_PORT = os.getenv("DB_PORT", "5432")

     @classmethod
     def get_dsn(cls) -> str:
         """
         Возвращает строку подключения к БД в формате DSN.
         Пример: postgresql://user:password@localhost:5432/dbname
         """
         return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"