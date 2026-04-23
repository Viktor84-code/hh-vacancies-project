"""
Точка входа в программу.
Получает данные о компаниях и вакансиях с hh.ru,
сохраняет в PostgreSQL и предоставляет интерфейс для работы.
"""

from src.api.hh_api import HHApi
from src.db.db_creator import DBCreator
from src.db.db_manager import DBManager
from src.utils.config import Config


def main():
    """Основная функция программы."""
    print("🚀 Запуск курсовой работы по БД")

    # 1. Получаем данные с hh.ru
    print("\n1. Получение данных о компаниях и вакансиях с hh.ru...")
    hh = HHApi()
    employers = hh.get_employers()

    if not employers:
        print("  Не удалось загрузить компании. Проверьте подключение к интернету.")
        return

    # 2. Создаём БД и таблицы
    print("\n2. Создание базы данных и таблиц...")
    creator = DBCreator()
    creator.create_database()
    creator.create_tables()

    # 3. Заполняем таблицы данными
    print("\n3. Заполнение таблиц...")
    conn = None
    cur = None
    try:
        import psycopg2

        conn = psycopg2.connect(Config.get_dsn())
        cur = conn.cursor()

        # Очищаем таблицы перед заполнением
        cur.execute("TRUNCATE vacancies CASCADE")
        cur.execute("TRUNCATE companies CASCADE")

        # Заполняем компании
        for emp in employers:
            cur.execute(
                """
                INSERT INTO companies (id, name, url, description)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """,
                (emp["id"], emp["name"], emp["url"], emp["description"]),
            )

            # Заполняем вакансии
            vacancies = hh.get_vacancies(emp["id"])
            for vac in vacancies:
                cur.execute(
                    """
                    INSERT INTO vacancies (id, company_id, name, url, salary_from, salary_to, salary_currency)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """,
                    (
                        vac["id"],
                        emp["id"],
                        vac["name"],
                        vac["url"],
                        vac["salary_from"],
                        vac["salary_to"],
                        vac["salary_currency"],
                    ),
                )

        conn.commit()
        print("  Данные успешно загружены в БД")
    except Exception as e:
        print(f"  Ошибка при загрузке данных: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    creator.close()

    # 4. Работа с DBManager
    print("\n4. Работа с данными через DBManager")
    db_manager = DBManager(Config.get_dsn())

    # Интерфейс пользователя
    while True:
        print("\n" + "=" * 50)
        print("Доступные команды:")
        print("1 - Компании и количество вакансий")
        print("2 - Все вакансии")
        print("3 - Средняя зарплата")
        print("4 - Вакансии с зарплатой выше средней")
        print("5 - Поиск по ключевому слову")
        print("0 - Выход")

        choice = input("\nВведите номер команды: ")

        if choice == "0":
            break
        elif choice == "1":
            results = db_manager.get_companies_and_vacancies_count()
            print("\nКомпании и количество вакансий:")
            for name, count in results:
                print(f"  {name}: {count} вакансий")
        elif choice == "2":
            results = db_manager.get_all_vacancies()
            print("\nВсе вакансии:")
            for row in results:
                print(
                    f"  {row[0]} - {row[1]} (зп: {row[2]} - {row[3]}, ссылка: {row[4]})"
                )
        elif choice == "3":
            avg = db_manager.get_avg_salary()
            print(f"\nСредняя зарплата по всем вакансиям: {avg:.2f}")
        elif choice == "4":
            results = db_manager.get_vacancies_with_higher_salary()
            print("\nВакансии с зарплатой выше средней:")
            for name, title, salary, url in results:
                print(f"  {name} - {title}: {salary:.2f} ({url})")
        elif choice == "5":
            keyword = input("Введите ключевое слово для поиска: ")
            results = db_manager.get_vacancies_with_keyword(keyword)
            print(f"\nВакансии, содержащие '{keyword}':")
            for name, title, url in results:
                print(f"  {name} - {title} ({url})")
        else:
            print("  Неверная команда. Попробуйте снова.")

    db_manager.close()
    print("\n🚀 Программа завершена. До свидания!")


if __name__ == "__main__":
    main()
