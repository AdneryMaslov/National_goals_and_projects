import pandas as pd
from typing import Optional, List, Dict, Any, Tuple
import re
from datetime import date

from app.core.database import get_db_pool
from asyncpg import Connection



async def get_or_create_generic_id(conn: Connection, table_name: str, name: str, parent_id_column: str = None,
                                   parent_id: int = None) -> int:
    """Универсальная функция: получает ID по имени. Если нет - создает."""
    # ... (эта функция остается без изменений)
    if parent_id_column and parent_id is not None:
        query = f"SELECT id FROM {table_name} WHERE name = $1 AND {parent_id_column} = $2"
        record_id = await conn.fetchval(query, name, parent_id)
        if record_id: return record_id
        insert_query = f"INSERT INTO {table_name} (name, {parent_id_column}) VALUES ($1, $2) RETURNING id"
        return await conn.fetchval(insert_query, name, parent_id)
    else:
        query = f"SELECT id FROM {table_name} WHERE name = $1"
        record_id = await conn.fetchval(query, name)
        if record_id: return record_id
        insert_query = f"INSERT INTO {table_name} (name) VALUES ($1) RETURNING id"
        return await conn.fetchval(insert_query, name)


async def save_parsed_data(
        metadata: dict,
        monthly_df: pd.DataFrame,
        yearly_df: pd.DataFrame
):
    """
    УМНАЯ ВЕРСИЯ: Находит индикатор по базовому имени (без скобок)
    и сохраняет для него спарсенные значения.
    """
    pool = await get_db_pool()
    if pool is None:
        raise ConnectionError("Пул соединений с БД не инициализирован.")

    original_indicator_name = metadata.get("name")
    if not original_indicator_name:
        raise ValueError("Имя индикатора отсутствует в метаданных.")

    # --- НАЧАЛО ИЗМЕНЕНИЙ ---

    # 2. Очищаем имя от текста в скобках в конце строки
    base_indicator_name = re.sub(r'\s*\([^)]*\)\s*$', '', original_indicator_name).strip()

    print(f"Оригинальное имя: '{original_indicator_name}'")
    if base_indicator_name != original_indicator_name:
        print(f"Базовое имя для поиска: '{base_indicator_name}'")
    else:
        print("Базовое имя совпадает с оригинальным.")

    async with pool.acquire() as conn:
        async with conn.transaction():

            # 3. Ищем ID существующего индикатора сначала по БАЗОВОМУ имени
            indicator_id = await conn.fetchval("SELECT id FROM indicators WHERE name = $1", base_indicator_name)

            # 4. Если по базовому не нашли, на всякий случай ищем по полному имени
            if not indicator_id:
                indicator_id = await conn.fetchval("SELECT id FROM indicators WHERE name = $1", original_indicator_name)
                if not indicator_id:
                    raise ValueError(
                        f"Индикатор с базовым названием '{base_indicator_name}' или полным '{original_indicator_name}' не найден в справочнике.")

            # 5. Обновляем метаданные у НАЙДЕННОГО индикатора
            await conn.execute("UPDATE indicators SET last_parsed_at = NOW() WHERE id = $1", indicator_id)
            # --- КОНЕЦ ИЗМЕНЕНИЙ ---

            # ... (остальная часть функции для сохранения данных остается без изменений) ...
            if yearly_df is not None and not yearly_df.empty:
                unique_regions_yr = yearly_df['region_name'].unique()
                region_ids_yr = {name: await get_or_create_generic_id(conn, 'regions', name) for name in
                                 unique_regions_yr}

                yearly_df['indicator_id'] = indicator_id
                yearly_df['region_id'] = yearly_df['region_name'].map(region_ids_yr)

                yearly_records = [tuple(x) for x in
                                  yearly_df[['indicator_id', 'region_id', 'year', 'yearly_value']].to_numpy()]
                await conn.executemany(
                    """
                    INSERT INTO indicator_yearly_values (indicator_id, region_id, year, yearly_value) 
                    VALUES ($1, $2, $3, $4) 
                    ON CONFLICT (indicator_id, region_id, year) DO UPDATE SET yearly_value = EXCLUDED.yearly_value
                    """,
                    yearly_records
                )

            if monthly_df is not None and not monthly_df.empty:
                unique_regions_mo = monthly_df['region_name'].unique()
                region_ids_mo = {name: await get_or_create_generic_id(conn, 'regions', name) for name in
                                 unique_regions_mo}

                monthly_df['indicator_id'] = indicator_id
                monthly_df['region_id'] = monthly_df['region_name'].map(region_ids_mo)

                monthly_records = [tuple(x) for x in
                                   monthly_df[['indicator_id', 'region_id', 'value_date', 'measured_value']].to_numpy()]
                await conn.executemany(
                    """
                    INSERT INTO indicator_monthly_values (indicator_id, region_id, value_date, measured_value) 
                    VALUES ($1, $2, $3, $4) 
                    ON CONFLICT (indicator_id, region_id, value_date) DO UPDATE SET measured_value = EXCLUDED.measured_value
                    """,
                    monthly_records
                )

    print(f"Обработка для индикатора '{original_indicator_name}' завершена.")


async def save_budget_data(budget_data: List[Dict[str, Any]]) -> Tuple[int, int]:
    """
    Сохраняет данные о бюджетах в базу данных.
    Автоматически создает недостающие регионы и проекты в справочниках.
    """
    pool = await get_db_pool()
    if pool is None:
        raise ConnectionError("Пул соединений с БД не инициализирован.")

    added_count = 0
    updated_count = 0

    async with pool.acquire() as conn:
        # Кэшируем ID для уменьшения количества запросов к БД
        regions_cache = {r['name']: r['id'] for r in await conn.fetch("SELECT id, name FROM regions")}
        projects_cache = {p['name']: p['id'] for p in await conn.fetch("SELECT id, name FROM national_projects")}

        async with conn.transaction():
            for item in budget_data:
                region_name = item.get("region_name")
                project_name = item.get("project_name")

                if not region_name or not project_name:
                    continue

                # --- ИЗМЕНЕНИЕ ЗДЕСЬ: Форматируем название проекта, добавляя префикс и кавычки ---

                # Изначально берем имя как есть
                formatted_project_name = project_name.strip()

                # Если у имени нет префикса "НП «", добавляем его
                if not formatted_project_name.startswith('НП «'):
                    formatted_project_name = f"НП «{formatted_project_name}»"

                # --- КОНЕЦ ИЗМЕНЕНИЙ ---

                # Проверяем и создаем регион, если его нет
                region_id = regions_cache.get(region_name)
                if not region_id:
                    print(f"INFO: Регион '{region_name}' не найден. Создание новой записи...")
                    region_id = await get_or_create_generic_id(conn, 'regions', region_name)
                    regions_cache[region_name] = region_id  # Обновляем кэш

                # Проверяем и создаем проект, если его нет, используя отформатированное имя
                project_id = projects_cache.get(formatted_project_name)
                if not project_id:
                    print(f"INFO: Проект '{formatted_project_name}' не найден. Создание новой записи...")
                    project_id = await get_or_create_generic_id(conn, 'national_projects', formatted_project_name)
                    projects_cache[formatted_project_name] = project_id  # Обновляем кэш

                query = """
                    INSERT INTO project_budgets (
                        region_id, project_id, relevance_date, 
                        amount_allocated, amount_executed, execution_percentage
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (region_id, project_id, relevance_date) 
                    DO UPDATE SET 
                        amount_allocated = EXCLUDED.amount_allocated,
                        amount_executed = EXCLUDED.amount_executed,
                        execution_percentage = EXCLUDED.execution_percentage
                    RETURNING (xmax = 0) AS inserted;
                """

                try:
                    relevance_date = date.fromisoformat(item['relevance_date'])

                    result = await conn.fetchrow(
                        query,
                        region_id,
                        project_id,
                        relevance_date,
                        item.get('amount_allocated'),
                        item.get('amount_executed'),
                        item.get('execution_percentage')
                    )

                    if result and result['inserted']:
                        added_count += 1
                    else:
                        updated_count += 1

                except Exception as e:
                    print(f"Ошибка при обработке записи для {formatted_project_name} в {region_name}: {e}")

    return added_count, updated_count

