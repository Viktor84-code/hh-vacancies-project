import psycopg2
import pytest

from src.db.db_creator import DBCreator
from src.utils.config import Config


@pytest.fixture
def db_creator():
    """Фикстура: создаёт временную БД и возвращает DBCreator."""
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

    # Удаляем тестовую базу, если есть
    cur.execute("DROP DATABASE IF EXISTS test_hh_vacancies")
    cur.close()
    conn.close()

    # Создаём экземпляр DBCreator
    original_db_name = Config.DB_NAME
    Config.DB_NAME = "test_hh_vacancies"

    creator = DBCreator()
    yield creator

    # Чистим после тестов
    creator.close()
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


def test_create_database(db_creator):
    """Тест: создание базы данных."""
    db_creator.create_database()
    # Проверяем, что база существует
    conn = psycopg2.connect(
        dbname="postgres",
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        host=Config.DB_HOST,
        port=Config.DB_PORT,
    )
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'test_hh_vacancies'")
    assert cur.fetchone() is not None
    cur.close()
    conn.close()


def test_create_tables(db_creator):
    """Тест: создание таблиц."""
    db_creator.create_database()
    db_creator.create_tables()

    # Проверяем, что таблицы существуют
    conn = psycopg2.connect(
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        host=Config.DB_HOST,
        port=Config.DB_PORT,
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name IN ('companies', 'vacancies')
    """)
    tables = {row[0] for row in cur.fetchall()}
    assert "companies" in tables
    assert "vacancies" in tables
    cur.close()
    conn.close()


def test_create_database_already_exists(db_creator):
    """Тест: создание базы, которая уже существует."""
    db_creator.create_database()  # первый раз
    db_creator.create_database()  # второй раз — должна быть уже создана


def test_create_tables_already_exists(db_creator):
    """Тест: создание таблиц, которые уже существуют."""
    db_creator.create_database()
    db_creator.create_tables()  # первый раз
    db_creator.create_tables()  # второй раз — должны быть уже созданы


def test_create_database_handles_exception(monkeypatch):
    """Тест: при ошибке подключения исключение перехватывается, программа не падает."""
    import psycopg2

    from src.db.db_creator import DBCreator

    def mock_connect_fail(*args, **kwargs):
        raise psycopg2.OperationalError("Fake connection error")

    # Подменяем psycopg2.connect на фальшивый, который всегда падает
    monkeypatch.setattr(psycopg2, "connect", mock_connect_fail)

    creator = DBCreator()
    # Эти методы не должны выбросить исключение (оно ловится внутри)
    creator.create_database()
    creator.create_tables()
    creator.close()
