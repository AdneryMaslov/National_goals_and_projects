# import_news.py
import asyncio
import asyncpg
import json
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import date


# --- НАСТРОЙКИ ---
@dataclass
class DBSettings:
    user: str = "postgres"
    password: str = "mastdmastd"
    host: str = "localhost"
    port: int = 5433
    database: str = "goals_n_projects"


JSON_FILE_PATH = "filtered_news.json"

TYPO_MAP = {
    "РЕАЛИЗАЦИЯ ПОТЕНЦИАЛА КАЖДОГО ЧЕЛОВЕКА, РАЗВИТИЕ ЕГО ТАЛАНТОВ, ВОСПИТАНИЕ ПАТРИОTIЧНОЙ И СОЦИАЛЬНО ОТВЕТСТВЕННОЙ ЛИЧНОСТИ":
    "РЕАЛИЗАЦИЯ ПОТЕНЦИАЛА КАЖДОГО ЧЕЛОВЕКА, РАЗВИТИЕ ЕГО ТАЛАНТОВ, ВОСПИТАНИЕ ПАТРИОТИЧНОЙ И СОЦИАЛЬНО ОТВЕТСТВЕННОЙ ЛИЧНОСТИ"
}


async def main():
    """
    Основная функция для импорта новостей из JSON-файла в базу данных.
    """
    settings = DBSettings()
    conn = None
    try:
        conn = await asyncpg.connect(
            user=settings.user,
            password=settings.password,
            host=settings.host,
            port=settings.port,
            database=settings.database
        )
        print("✅ Успешное подключение к базе данных.")

        # 1. Загружаем данные из JSON-файла
        try:
            with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            print(f"📄 Успешно загружено {len(news_data)} новостей из файла.")
        except FileNotFoundError:
            print(f"❌ ОШИБКА: Файл '{JSON_FILE_PATH}' не найден.")
            return
        except json.JSONDecodeError:
            print(f"❌ ОШИБКА: Не удалось прочитать JSON из файла '{JSON_FILE_PATH}'.")
            return

        # 2. Начинаем транзакцию для безопасного импорта
        async with conn.transaction():
            print("\n--- Начало импорта новостей ---")

            regions_cache = {r['name']: r['id'] for r in await conn.fetch("SELECT id, name FROM regions")}
            goals_cache = {g['name'].upper(): g['id'] for g in await conn.fetch("SELECT id, name FROM national_goals")}

            inserted_count = 0
            updated_count = 0
            processed_count = 0

            for news_item in news_data:
                processed_count += 1
                region_name = news_item.get("region_name")
                goal_name = news_item.get("national_goal")

                region_id = regions_cache.get(region_name)
                if not region_id:
                    print(f"  -> Регион '{region_name}' не найден, создаем новый...")
                    region_id = await conn.fetchval(
                        "INSERT INTO regions (name) VALUES ($1) ON CONFLICT (name) DO UPDATE SET name=EXCLUDED.name RETURNING id",
                        region_name)
                    regions_cache[region_name] = region_id

                if not goal_name:
                    print(f"  ⚠️ Пропуск новости: отсутствует название нац. цели.")
                    continue

                # Применяем исправление опечатки
                goal_name_upper = goal_name.upper()
                if goal_name_upper in TYPO_MAP:
                    goal_name = TYPO_MAP[goal_name_upper]
                    goal_name_upper = goal_name.upper()

                goal_id = goals_cache.get(goal_name_upper)
                if not goal_id:
                    print(f"  ⚠️ Пропуск новости: не найдена нац. цель '{goal_name}' в справочнике.")
                    continue

                project_ids = await conn.fetch(
                    "SELECT project_id FROM project_to_goal_mapping WHERE goal_id = $1",
                    goal_id
                )

                if not project_ids:
                    print(f"  ⚠️ Пропуск новости: для нац. цели '{goal_name}' не найдено связанных проектов.")
                    continue

                published_date_str = news_item.get("published_date")
                published_date_obj = date.fromisoformat(published_date_str) if published_date_str else None

                last_update_str = news_item.get("last_update")
                last_update_obj = date.fromisoformat(last_update_str) if last_update_str else None

                for record in project_ids:
                    project_id = record['project_id']

                    query = """
                        INSERT INTO project_activities (
                            project_id, region_id, title, activity_date, link, 
                            responsible_body, text, importance, last_update
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                        ON CONFLICT (link) DO UPDATE SET
                            title = EXCLUDED.title,
                            activity_date = EXCLUDED.activity_date,
                            responsible_body = EXCLUDED.responsible_body,
                            text = EXCLUDED.text,
                            importance = EXCLUDED.importance,
                            last_update = EXCLUDED.last_update
                        RETURNING (xmax = 0) AS inserted;
                    """

                    result = await conn.fetchrow(
                        query,
                        project_id,
                        region_id,
                        news_item.get("title"),
                        published_date_obj,
                        news_item.get("url"),
                        news_item.get("source_name"),
                        news_item.get("content"),
                        news_item.get("importance"),
                        last_update_obj
                    )

                    if result and result['inserted']:
                        inserted_count += 1
                    else:
                        updated_count += 1

            print("\n--- Импорт завершен ---")
            print(f"✅ Обработано новостей из файла: {processed_count}")
            print(f"✅ Добавлено новых записей в БД: {inserted_count}")
            print(f"🔄 Обновлено существующих записей: {updated_count}")

    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        print("--- Все изменения были отменены (откат транзакции) ---")
    finally:
        if conn:
            await conn.close()
            print("\n🔌 Соединение с базой данных закрыто.")


if __name__ == "__main__":
    print("--- Запуск скрипта для импорта новостей ---")
    asyncio.run(main())
