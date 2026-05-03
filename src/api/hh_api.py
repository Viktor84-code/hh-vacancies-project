"""
Модуль для работы с API hh.ru.
Получает данные о компаниях и их вакансиях.
"""

import json
import os
from typing import Any, Dict, List
import requests


class HHApi:
    """Класс для работы с данными из JSON-файла + твои компании."""

    def __init__(self, json_path: str = "data/hh_data.json"):
        self.json_path = json_path

    def _load_json(self) -> Dict[str, Any]:
        """Загружает JSON-файл."""
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"Файл {self.json_path} не найден!")
        with open(self.json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_employers(self) -> List[Dict[str, Any]]:
        """Извлекает компании из JSON + добавляет твои."""
        data = self._load_json()
        items = data.get("items", [])

        # Собираем компании из файла Skypro
        employers_dict = {}
        for item in items:
            emp = item.get("employer")
            if emp and emp.get("id") and emp.get("id") not in employers_dict:
                employers_dict[emp["id"]] = {
                    "id": int(emp["id"]),
                    "name": emp.get("name", "Unknown"),
                    "url": emp.get("alternate_url", ""),
                    "description": "",
                }

        # ТВОИ КОМПАНИИ (добавляем, если их нет)
        your_employers = [
            {
                "id": 1074173,
                "name": "Георг Полимер",
                "url": "https://hh.ru/employer/1074173",
                "description": "Экструзия, производство полимеров",
            },
            {
                "id": 39305,
                "name": "Газпром Нефть",
                "url": "https://hh.ru/employer/39305",
                "description": "Нефтегазовая компания",
            },
            {
                "id": 20465,
                "name": "ООО МАСТЕРФУД",
                "url": "https://hh.ru/employer/20465",
                "description": "Производство продуктов питания",
            },
            {
                "id": 4181,
                "name": "ВТБ",
                "url": "https://hh.ru/employer/4181",
                "description": "Банк",
            },
            {
                "id": 2748,
                "name": "Ростелеком",
                "url": "https://hh.ru/employer/2748",
                "description": "Телеком-оператор",
            },
            {
                "id": 3127,
                "name": "Мегафон",
                "url": "https://hh.ru/employer/3127",
                "description": "Телеком-оператор",
            },
            {
                "id": 2180,
                "name": "Ozon",
                "url": "https://hh.ru/employer/2180",
                "description": "Маркетплейс",
            },
        ]

        for emp in your_employers:
            if str(emp["id"]) not in employers_dict:
                employers_dict[str(emp["id"])] = emp

        print(f"  Всего компаний: {len(employers_dict)}")
        for emp in employers_dict.values():
            print(f"    {emp['name']}")

        return list(employers_dict.values())

    def get_vacancies(self, employer_id: str) -> List[Dict[str, Any]]:
        """Возвращает вакансии для компании (из файла или тестовые)."""
        data = self._load_json()
        items = data.get("items", [])

        # Ищем вакансии в файле
        vacancies = []
        for item in items:
            emp = item.get("employer")
            if emp and str(emp.get("id")) == str(employer_id):
                salary = item.get("salary")
                vacancies.append(
                    {
                        "id": item.get("id"),
                        "name": item.get("name"),
                        "url": item.get("alternate_url"),
                        "salary_from": salary.get("from") if salary else None,
                        "salary_to": salary.get("to") if salary else None,
                        "salary_currency": salary.get("currency") if salary else None,
                    }
                )

        # Если вакансий нет — тестовые для твоих компаний
        if not vacancies and employer_id in [
            "1074173",
            "39305",
            "20465",
            "4181",
            "2748",
            "3127",
            "2180",
        ]:
            return [
                {
                    "id": 1,
                    "name": "Разработчик Python",
                    "url": "https://hh.ru/vacancy/1",
                    "salary_from": 150000,
                    "salary_to": 250000,
                    "salary_currency": "RUR",
                },
                {
                    "id": 2,
                    "name": "Аналитик данных",
                    "url": "https://hh.ru/vacancy/2",
                    "salary_from": 120000,
                    "salary_to": 200000,
                    "salary_currency": "RUR",
                },
            ]

        return vacancies

    def fetch_real_vacancies(self, employer_id: str) -> List[Dict]:
        """Пытается получить реальные вакансии из API."""
        url = f"https://api.hh.ru/vacancies?employer_id={employer_id}&per_page=10"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            return response.json().get("items", [])
        return []
