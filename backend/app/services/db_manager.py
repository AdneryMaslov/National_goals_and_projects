# /app/services/db_manager.py (ИСПРАВЛЕННАЯ ВЕРСИЯ)

import pandas as pd
from app.core.database import get_db_pool
from asyncpg import Connection  # Импортируем тип Connection для подсказок


# --- ИЗМЕНЕНИЕ №1: Функция теперь принимает объект подключения `conn`, а не `pool` ---
async def get_or_create_id(conn: Connection, table_name: str, name: str) -> int:
    """Получает ID записи по имени, если нет - создает и возвращает новый ID."""
    # Мы больше не берем новое подключение из пула, а используем существующее
    record_id = await conn.fetchval(f"SELECT id FROM {table_name} WHERE name = $1", name)
    if record_id:
        return record_id
    return await conn.fetchval(f"INSERT INTO {table_name} (name) VALUES ($1) RETURNING id", name)


async def save_parsed_data(metadata: dict, monthly_df: pd.DataFrame, yearly_df: pd.DataFrame):
    """Оркестрирует сохранение всех спарсенных данных в базу данных."""
    pool = await get_db_pool()
    if pool is None:
        raise ConnectionError("Пул соединений с БД не инициализирован.")

    # Используем 'pool.acquire()' для получения одного подключения на всю операцию
    async with pool.acquire() as conn:
        # --- ИЗМЕНЕНИЕ №2: Передаем `conn` в get_or_create_id ---
        indicator_id = await get_or_create_id(conn, 'indicators', metadata.get("name"))

        # Обновляем метаданные индикатора (unit, desired_direction)
        await conn.execute(
            "UPDATE indicators SET unit = $1, desired_direction = $2 WHERE id = $3",
            metadata.get("unit"), metadata.get("desired_direction", 'lower'), indicator_id
        )

        async with conn.transaction():
            # 1. Готовим и сохраняем месячные данные
            if not monthly_df.empty:
                # --- ИЗМЕНЕНИЕ №3: Передаем `conn` в get_or_create_id для регионов ---
                unique_regions = monthly_df['region_name'].unique()
                region_ids = {name: await get_or_create_id(conn, 'regions', name) for name in unique_regions}

                monthly_df['indicator_id'] = indicator_id
                monthly_df['region_id'] = monthly_df['region_name'].map(region_ids)

                monthly_records = [tuple(x) for x in
                                   monthly_df[['indicator_id', 'region_id', 'value_date', 'measured_value']].to_numpy()]

                # Используем ON CONFLICT, чтобы не было дубликатов
                await conn.executemany(
                    """INSERT INTO indicator_monthly_values (indicator_id, region_id, value_date, measured_value) 
                       VALUES ($1, $2, $3, $4) 
                       ON CONFLICT (indicator_id, region_id, value_date) DO NOTHING""",
                    monthly_records
                )

            # 2. Готовим и сохраняем годовые данные
            if not yearly_df.empty:
                # --- ИЗМЕНЕНИЕ №4: Передаем `conn` в get_or_create_id для регионов ---
                unique_regions = yearly_df['region_name'].unique()
                region_ids = {name: await get_or_create_id(conn, 'regions', name) for name in unique_regions}

                yearly_df['indicator_id'] = indicator_id
                yearly_df['region_id'] = yearly_df['region_name'].map(region_ids)

                yearly_records = [tuple(x) for x in
                                  yearly_df[['indicator_id', 'region_id', 'year', 'yearly_value']].to_numpy()]

                # Используем ON CONFLICT, чтобы не было дубликатов
                await conn.executemany(
                    """INSERT INTO indicator_yearly_values (indicator_id, region_id, year, yearly_value) 
                       VALUES ($1, $2, $3, $4) 
                       ON CONFLICT (indicator_id, region_id, year) DO NOTHING""",
                    yearly_records
                )

    print(
        f"Обработка завершена. Добавлено/проигнорировано {len(monthly_df)} месячных и {len(yearly_df)} годовых записей.")
    return len(monthly_df), len(yearly_df)