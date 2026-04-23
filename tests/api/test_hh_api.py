import pytest
import os
from src.api.hh_api import HHApi


def test_get_employers_returns_list():
    """Тест: get_employers возвращает список компаний."""
    # Строим правильный путь к JSON относительно корня проекта
    json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'hh_data.json')
    api = HHApi(json_path=json_path)  # 👈 передаём путь явно
    employers = api.get_employers()
    assert isinstance(employers, list)
    assert len(employers) > 0
    assert 'id' in employers[0]
    assert 'name' in employers[0]


def test_get_vacancies_returns_list():
    """Тест: get_vacancies возвращает список вакансий."""
    json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'hh_data.json')
    api = HHApi(json_path=json_path)
    employers = api.get_employers()
    if employers:
        vacancies = api.get_vacancies(employers[0]['id'])
        assert isinstance(vacancies, list)
