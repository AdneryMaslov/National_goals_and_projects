# app/services/db_manager.py

import pandas as pd
from typing import Optional
from app.core.database import get_db_pool
from asyncpg import Connection
import re  # 1. Импортируем модуль для регулярных выражений


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