"""
Модуль с классом DBManager для работы с данными в БД.
"""

import psycopg2
from typing import List, Tuple, Any
from src.utils.config import Config


class DBManager:
    """Класс для работы с данными в PostgreSQL."""

    def __init__(self, dsn: str = None):
        """Подключается к БД."""
        # Временно используем параметры вместо DSN из-за бага psycopg2 в Windows
        if dsn:
            # Пробуем через DSN (если передан)
            try:
                self.conn = psycopg2.connect(dsn)
            except UnicodeDecodeError:
                # Если DSN ломается, переключаемся на параметры
                self.conn = psycopg2.connect(
                    dbname=Config.DB_NAME,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    host=Config.DB_HOST,
                    port=Config.DB_PORT
                )
        else:
            # Если DSN не передан, используем параметры
            self.conn = psycopg2.connect(
                dbname=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                host=Config.DB_HOST,
                port=Config.DB_PORT
            )
        self.cur = self.conn.cursor()

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """Возвращает список компаний и количество вакансий у каждой."""
        self.cur.execute("""
            SELECT c.name, COUNT(v.id) as vacancies_count
            FROM companies c
            LEFT JOIN vacancies v ON c.id = v.company_id
            GROUP BY c.name
            ORDER BY vacancies_count DESC
        """)
        return self.cur.fetchall()

    def get_all_vacancies(self) -> List[Tuple[str, str, int, int, str]]:
        """Возвращает список всех вакансий."""
        self.cur.execute("""
            SELECT c.name, v.name, v.salary_from, v.salary_to, v.url
            FROM vacancies v
            JOIN companies c ON v.company_id = c.id
        """)
        return self.cur.fetchall()

    def get_avg_salary(self) -> float:
        """Возвращает среднюю зарплату по всем вакансиям."""
        self.cur.execute("""
            SELECT AVG((salary_from + salary_to) / 2)
            FROM vacancies
            WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL
        """)
        result = self.cur.fetchone()[0]
        return float(result) if result else 0.0

    def get_vacancies_with_higher_salary(self) -> List[Tuple[str, str, float, str]]:
        """Возвращает список вакансий с зарплатой выше средней."""
        avg_salary = self.get_avg_salary()
        self.cur.execute("""
            SELECT c.name, v.name, (v.salary_from + v.salary_to) / 2 as avg_salary, v.url
            FROM vacancies v
            JOIN companies c ON v.company_id = c.id
            WHERE (v.salary_from + v.salary_to) / 2 > %s
            ORDER BY avg_salary DESC
        """, (avg_salary,))
        return self.cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple[str, str, str]]:
        """Возвращает список вакансий, в названии которых есть ключевое слово."""
        self.cur.execute("""
            SELECT c.name, v.name, v.url
            FROM vacancies v
            JOIN companies c ON v.company_id = c.id
            WHERE v.name ILIKE %s
        """, (f"%{keyword}%",))
        return self.cur.fetchall()

    def close(self):
        """Закрывает соединение с БД."""
        self.cur.close()
        self.conn.close()
