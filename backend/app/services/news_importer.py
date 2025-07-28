import json
import asyncpg
from typing import Tuple
from datetime import date

# Константа JSON_FILE_PATH больше не нужна, так как файл будет передаваться напрямую
# JSON_FILE_PATH = "app/services/filtered_news.json"

TYPO_MAP = {
    "РЕАЛИЗАЦИЯ ПОТЕНЦИАЛА КАЖДОГО ЧЕЛОВЕКА, РАЗВИТИЕ ЕГО ТАЛАНТОВ, ВОСПИТАНИЕ ПАТРИОTIЧНОЙ И СОЦИАЛЬНО ОТВЕТСТВЕННОЙ ЛИЧНОСТИ":
    "РЕАЛИЗАЦИЯ ПОТЕНЦИАЛА КАЖДОГО ЧЕЛОВЕКА, РАЗВИТИЕ ЕГО ТАЛАНТОВ, ВОСПИТАНИЕ ПАТРИОТИЧНОЙ И СОЦИАЛЬНО ОТВЕТСТВЕННОЙ ЛИЧНОСТИ"
}


# --- ИЗМЕНЕНИЕ 1: Функция теперь принимает содержимое файла (в байтах) ---
async def import_news_from_upload(pool: asyncpg.Pool, file_content: bytes) -> Tuple[int, int, int]:
    """
    Импортирует новости из загруженного JSON-файла в базу данных.
    """
    # --- ИЗМЕНЕНИЕ 2: Загружаем JSON из содержимого файла, а не из диска ---
    news_data = json.loads(file_content)

    inserted_count = 0
    updated_count = 0
    processed_count = 0

    async with pool.acquire() as conn:
        async with conn.transaction():
            regions_cache = {r['name']: r['id'] for r in await conn.fetch("SELECT id, name FROM regions")}
            goals_cache = {g['name'].upper(): g['id'] for g in await conn.fetch("SELECT id, name FROM national_goals")}

            # Проверяем, есть ли ключ "results" в JSON
            for news_item in news_data.get("results", []):
                processed_count += 1
                region_name = news_item.get("region_name")
                goal_name = news_item.get("national_goal")

                region_id = regions_cache.get(region_name)
                if not region_id:
                    region_id = await conn.fetchval(
                        "INSERT INTO regions (name) VALUES ($1) ON CONFLICT (name) DO UPDATE SET name=EXCLUDED.name RETURNING id",
                        region_name)
                    regions_cache[region_name] = region_id

                if not goal_name:
                    continue

                goal_name_upper = goal_name.upper()
                if goal_name_upper in TYPO_MAP:
                    goal_name = TYPO_MAP[goal_name_upper]
                    goal_name_upper = goal_name.upper()

                goal_id = goals_cache.get(goal_name_upper)
                if not goal_id:
                    continue

                project_ids = await conn.fetch(
                    "SELECT project_id FROM project_to_goal_mapping WHERE goal_id = $1",
                    goal_id
                )
                if not project_ids:
                    continue

                published_date_obj = date.fromisoformat(news_item["published_date"]) if news_item.get(
                    "published_date") else None
                last_update_obj = date.fromisoformat(news_item["last_update"]) if news_item.get("last_update") else None

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
                        query, project_id, region_id, news_item.get("title"),
                        published_date_obj, news_item.get("url"), news_item.get("source_name"),
                        news_item.get("content"), news_item.get("importance"), last_update_obj
                    )
                    if result and result['inserted']:
                        inserted_count += 1
                    else:
                        updated_count += 1

    return processed_count, inserted_count, updated_count