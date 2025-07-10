import asyncpg
import json
import os
import asyncio
from dotenv import load_dotenv
from datetime import datetime  # 1. Импортируем модуль datetime

# --- НАСТРОЙКИ ДЛЯ ЗАГРУЗКИ ---
TARGET_PROJECT_NAME = "НП «Кадры»"
TARGET_REGION_NAME = "Псковская область"
# --------------------------------

load_dotenv()


async def main():
    conn = None
    try:
        # --- Подключение и получение ID ---
        conn = await asyncpg.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        print("✅ Подключение к базе данных успешно.")

        project_id = await conn.fetchval("SELECT id FROM national_projects WHERE name = $1", TARGET_PROJECT_NAME)
        if not project_id:
            print(f"❌ Ошибка: Национальный проект '{TARGET_PROJECT_NAME}' не найден в базе данных.")
            return

        region_id = await conn.fetchval("SELECT id FROM regions WHERE name = $1", TARGET_REGION_NAME)
        if not region_id:
            print(f"❌ Ошибка: Регион '{TARGET_REGION_NAME}' не найден в базе данных.")
            return

        print(f"Найден ID для проекта '{TARGET_PROJECT_NAME}': {project_id}")
        print(f"Найден ID для региона '{TARGET_REGION_NAME}': {region_id}")

        # --- Чтение JSON-файла ---
        with open('Новости.json', 'r', encoding='utf-8') as f:
            all_activities = json.load(f)

        if not all_activities:
            print(f"⚠️ Файл Новости.json пуст.")
            return

        # --- ИЗМЕНЕНИЕ ЗДЕСЬ: Готовим данные для вставки с правильным типом даты ---
        records_to_insert = []
        for activity in all_activities:
            date_str = activity.get('date', '').split(' ')[0]  # Берем только дату, например "07.07.2025"
            activity_date_obj = None
            if date_str:
                try:
                    # 2. Преобразуем строку "ДД.ММ.ГГГГ" в объект даты
                    activity_date_obj = datetime.strptime(date_str, '%d.%m.%Y').date()
                except ValueError:
                    print(f"Предупреждение: не удалось распознать дату '{date_str}'. Поле останется пустым.")
                    activity_date_obj = None

            records_to_insert.append(
                # 3. Передаем в кортеж именно объект даты, а не строку
                (project_id, region_id, activity['title'], activity_date_obj, activity.get('link'))
            )

        # --- Загружаем данные в таблицу ---
        await conn.executemany(
            """
            INSERT INTO project_activities (project_id, region_id, title, activity_date, link)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (link) DO NOTHING;
            """,
            records_to_insert
        )

        print(
            f"✅ Успешно проверено {len(records_to_insert)} мероприятий. Новые уникальные мероприятия добавлены в базу.")

    except json.JSONDecodeError as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: Файл 'Новости.json' имеет неверный формат.")
        print(f"   Детали ошибки: {e}")
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
    finally:
        if conn:
            await conn.close()
            print("Соединение с базой данных закрыто.")


if __name__ == "__main__":
    asyncio.run(main())