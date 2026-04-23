"""
Конфигурация для подключения к PostgreSQL.
Данные берутся из переменных окружения(.env файл).
"""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Настройки подключения к базе данных."""
    # Принудительно переводим в латиницу, убирая возможные кривые символы
    DB_NAME = os.getenv("DB_NAME", "hh_vacancies").encode("ascii", "ignore").decode()
    DB_USER = os.getenv("DB_USER", "postgres").encode("ascii", "ignore").decode()
    DB_PASSWORD = (
        os.getenv("DB_PASSWORD", "postgres").encode("ascii", "ignore").decode()
    )
    DB_HOST = os.getenv("DB_HOST", "localhost").encode("ascii", "ignore").decode()
    DB_PORT = os.getenv("DB_PORT", "5432").encode("ascii", "ignore").decode()

    @classmethod
    def get_dsn(cls) -> str:
        """Возвращает строку подключения к БД."""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
