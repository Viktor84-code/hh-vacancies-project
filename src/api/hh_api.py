"""
Модуль для работы с API hh.ru.
Получает данные о компаниях и их вакансиях.
"""

import requests
from typing import List, Dict, Any

from src.utils.config import Config

class HHApi:
    """Класс для получения данных с hh.ru."""

    BASE_URL = 'https://api.hh.ru'

    # Список компаний (ID с hh.ru)
    EMPLOYER_IDS = [
        "1740",  # Яндекс
        "78638",  # Т-Банк
        "3529",  # Сбер
        "1074173",  # Георг Полимер (производство, экструзия!) 🔥
        "39305",  # Газпром Нефть (IT + нефтегаз)
        "20465",  # ООО МАСТЕРФУД (IT для производства)
        "4181",  # Банк ВТБ
        "2748",  # Ростелеком (IT + связь)
        "3127",  # Мегафон ПАО
        "2180",  # Ozon
    ]

    def get_employers(self) -> List[Dict[str, Any]]:
        """Получает список работодателей по заранее заданным ID."""
        employers = []
        for emp_id in self.EMPLOYER_IDS:
            url = f"{self.BASE_URL}/employers/{emp_id}"
            try:
                response = requests.get(url)
                response.raise_for_status()
                employer_data = response.json()
                employers.append({
                    "id": employer_data.get("id"),
                    "name": employer_data.get("name"),
                    "url": employer_data.get("url"),
                    "description": employer_data.get("description", "")
                })
                print(f"  Загружена компания: {employer_data.get('name')}")
            except Exception as e:
                print(f"  Ошибка при загрузке компании {emp_id}: {e}")
        return employers

    def get_vacancies(self, employer_id: str) -> List[Dict[str, Any]]:
        """Получает список вакансий для конкретного работодателя."""
        vacancies = []
        url = f"{self.BASE_URL}/vacancies"
        params = {
            "employer_id": employer_id,
            "per_page": 20,  # не более 20 вакансий на компанию
            "only_with_salary": True  # только с зарплатой
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            for item in data.get("items", []):
                salary = item.get("salary")
                salary_from = salary.get("from") if salary else None
                salary_to = salary.get("to") if salary else None
                vacancies.append({
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "url": item.get("alternate_url"),
                    "salary_from": salary_from,
                    "salary_to": salary_to,
                    "salary_currency": salary.get("currency") if salary else None
                })
        except Exception as e:
            print(f"  Ошибка при загрузке вакансий для {employer_id}: {e}")
        return vacancies