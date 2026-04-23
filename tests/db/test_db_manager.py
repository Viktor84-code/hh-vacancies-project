import psycopg2
import pytest

from src.db.db_manager import DBManager
from src.utils.config import Config


@pytest.fixture
def db_manager():
    """Фикстура: создаёт временную БД и подключает DBManager."""
    # Подключаемся к стандартной БД postgres
    conn = psycopg2.connect(
        dbname="postgres",
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        host=Config.DB_HOST,
        port=Config.DB_PORT,
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Создаём тестовую базу
    cur.execute("DROP DATABASE IF EXISTS test_hh_vacancies")
    cur.execute("CREATE DATABASE test_hh_vacancies")
    cur.close()
    conn.close()

    # Временно меняем имя БД в конфиге
    original_db_name = Config.DB_NAME
    Config.DB_NAME = "test_hh_vacancies"

    # Создаём таблицы в тестовой БД
    from src.db.db_creator import DBCreator

    creator = DBCreator()
    creator.create_tables()
    creator.close()

    # Создаём экземпляр DBManager для тестов
    manager = DBManager()

    yield manager

    # Чистим после тестов
    manager.close()
    Config.DB_NAME = original_db_name

    # Удаляем тестовую базу
    conn = psycopg2.connect(
        dbname="postgres",
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        host=Config.DB_HOST,
        port=Config.DB_PORT,
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("DROP DATABASE IF EXISTS test_hh_vacancies")
    cur.close()
    conn.close()


def test_get_companies_and_vacancies_count(db_manager):
    """Тест: список компаний и количество вакансий."""
    db_manager.cur.execute(
        "INSERT INTO companies (id, name) VALUES (1, 'Test Company')"
    )
    db_manager.cur.execute(
        "INSERT INTO vacancies (id, company_id, name) VALUES (101, 1, 'Test Vacancy')"
    )
    db_manager.conn.commit()

    result = db_manager.get_companies_and_vacancies_count()
    assert len(result) == 1
    assert result[0][0] == "Test Company"
    assert result[0][1] == 1


def test_get_all_vacancies(db_manager):
    """Тест: список всех вакансий."""
    db_manager.cur.execute(
        "INSERT INTO companies (id, name) VALUES (1, 'Test Company')"
    )
    db_manager.cur.execute("""
        INSERT INTO vacancies (id, company_id, name, url)
        VALUES (101, 1, 'Test Vacancy', 'https://test.com')
    """)
    db_manager.conn.commit()

    result = db_manager.get_all_vacancies()
    assert len(result) == 1
    assert result[0][0] == "Test Company"
    assert result[0][1] == "Test Vacancy"


def test_get_avg_salary(db_manager):
    """Тест: средняя зарплата."""
    db_manager.cur.execute(
        "INSERT INTO companies (id, name) VALUES (1, 'Test Company')"
    )
    db_manager.cur.execute("""
        INSERT INTO vacancies (id, company_id, name, salary_from, salary_to)
        VALUES (101, 1, 'Test Vacancy', 100000, 200000)
    """)
    db_manager.conn.commit()

    avg = db_manager.get_avg_salary()
    assert avg == 150000.0


def test_get_vacancies_with_higher_salary(db_manager):
    """Тест: вакансии с зарплатой выше средней."""
    db_manager.cur.execute(
        "INSERT INTO companies (id, name) VALUES (1, 'Test Company')"
    )
    db_manager.cur.execute("""
        INSERT INTO vacancies (id, company_id, name, salary_from, salary_to)
        VALUES (101, 1, 'Junior', 100000, 200000)
    """)
    db_manager.cur.execute("""
        INSERT INTO vacancies (id, company_id, name, salary_from, salary_to)
        VALUES (102, 1, 'Senior', 200000, 300000)
    """)
    db_manager.conn.commit()

    result = db_manager.get_vacancies_with_higher_salary()
    # Средняя зарплата: (150000 + 250000) / 2 = 200000
    # Выше средней только Senior (250000)
    assert len(result) == 1
    assert "Senior" in result[0][1]


def test_get_vacancies_with_keyword(db_manager):
    """Тест: поиск по ключевому слову."""
    db_manager.cur.execute(
        "INSERT INTO companies (id, name) VALUES (1, 'Test Company')"
    )
    db_manager.cur.execute("""
        INSERT INTO vacancies (id, company_id, name)
        VALUES (101, 1, 'Python Developer')
    """)
    db_manager.cur.execute("""
        INSERT INTO vacancies (id, company_id, name)
        VALUES (102, 1, 'Java Developer')
    """)
    db_manager.conn.commit()

    result = db_manager.get_vacancies_with_keyword("Python")
    assert len(result) == 1
    assert "Python" in result[0][1]


def test_unicode_decode_error_fallback(monkeypatch):
    """Тест: при ошибке UnicodeDecodeError переключаемся на параметры."""
    import psycopg2

    from src.db.db_manager import DBManager

    original_connect = psycopg2.connect
    call_count = 0

    def mock_connect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # Первый вызов — через DSN (аргумент в *args)
            raise UnicodeDecodeError("utf-8", b"", 0, 1, "fake")
        # Второй вызов — через параметры (ключевые аргументы)
        return original_connect(*args, **kwargs)

    monkeypatch.setattr(psycopg2, "connect", mock_connect)
    db = DBManager(dsn="postgresql://postgres:postgres@localhost:5432/hh_vacancies")
    assert db.conn is not None
    db.close()
