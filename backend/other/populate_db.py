# populate_db.py

import asyncio
import pandas as pd
import asyncpg
import re
from app.core.database import settings

# --- Константы и настройки ---
CSV_FILE_PATH = 'table_csv_1.csv'
YEAR_COLUMNS = [str(year) for year in range(2021, 2031)] + ['2035']


# --- Вспомогательные функции ---

def clean_project_names(text: str) -> list[str]:
    """Очищает и разделяет строку с нацпроектами на список ТОЛЬКО по переносу строки."""
    if not isinstance(text, str) or text.strip() == '':
        return []
    return [name.strip() for name in text.split('\n') if name.strip()]


def map_desired_direction(text: str) -> str | None:
    """Преобразует тип показателя ('Прямой'/'Обратный') в флаг 'higher' или 'lower'."""
    if not isinstance(text, str):
        return None
    text = text.lower().strip()
    if text == 'прямой':
        return 'higher'
    if text == 'обратный':
        return 'lower'
    return None


# --- Основная логика скрипта ---

async def main():
    """Главная функция для подключения, обработки и загрузки данных."""
    conn = None
    try:
        conn = await asyncpg.connect(
            user=settings.db_user, password=settings.db_password,
            database=settings.db_name, host=settings.db_host, port=settings.db_port
        )
        print("✅ Соединение с базой данных установлено.")

        df = pd.read_csv(CSV_FILE_PATH, engine='python', sep=';')
        print("НАЗВАНИЯ СТОЛБЦОВ В ФАЙЛЕ:", list(df.columns))
        print(f"📖 Исходный файл содержит {len(df)} строк.")

        # Очистка данных
        print("🧹 Очистка данных от нумерации и префиксов...")
        df['Национальная цель'] = df['Национальная цель'].astype(str).str.replace(r'^\d+\.\s*', '',
                                                                                  regex=True).str.strip()
        df['Показатель'] = df['Показатель'].astype(str).str.replace(r'^\d+(\.\d+)*(\.?[а-я])?\.\s*', '',
                                                                    regex=True).str.strip()
        prefix_pattern = r'^((\d+(\.\d+)*(\.?[а-я])?\.\s*)|(Дополнительный:\s*))'
        df['Статистический индикатор'] = df['Статистический индикатор'].astype(str).str.replace(prefix_pattern, '',
                                                                                                regex=True).str.strip()
        print("✅ Данные успешно очищены. Все строки будут загружены.")

        # Итерация и загрузка данных
        for index, row in df.iterrows():
            if row.isnull().all():
                continue

            async with conn.transaction():
                try:
                    goal_name = str(row['Национальная цель']).strip()
                    goal_id = await conn.fetchval(
                        'INSERT INTO national_goals (name) VALUES ($1) ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name RETURNING id',
                        goal_name)

                    metric_name = str(row['Показатель']).strip()
                    metric_id = await conn.fetchval(
                        'INSERT INTO goal_metrics (name, goal_id) VALUES ($1, $2) ON CONFLICT (goal_id, name) DO UPDATE SET name = EXCLUDED.name RETURNING id',
                        metric_name, goal_id)

                    indicator_name = str(row['Статистический индикатор']).strip()
                    indicator_id = await conn.fetchval(
                        """
                        INSERT INTO indicators (name, metric_id, unit, desired_direction, source_url, periodicity, responsible_foiv, use_for_agent, indicator_type)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                        ON CONFLICT (name) DO UPDATE SET
                            metric_id = EXCLUDED.metric_id, unit = EXCLUDED.unit, desired_direction = EXCLUDED.desired_direction,
                            source_url = EXCLUDED.source_url, periodicity = EXCLUDED.periodicity,
                            responsible_foiv = EXCLUDED.responsible_foiv, use_for_agent = EXCLUDED.use_for_agent,
                            indicator_type = EXCLUDED.indicator_type
                        RETURNING id
                        """,
                        indicator_name, metric_id,
                        str(row.get('Единица измерения')) if pd.notna(row.get('Единица измерения')) else None,
                        map_desired_direction(row.get('Тип показателя')),
                        str(row.get('Ссылка')) if pd.notna(row.get('Ссылка')) else None,
                        str(row.get('Периодичность обновления')) if pd.notna(
                            row.get('Периодичность обновления')) else None,
                        str(row.get('Ответственный (ФОИВ)')) if pd.notna(row.get('Ответственный (ФОИВ)')) else None,
                        str(row.get('Использовать для агента')).lower() == 'да',
                        # --- ДОБАВЛЕНО: Чтение нового столбца ---
                        row.get('Тип индикатора').strip() if pd.notna(row.get('Тип индикатора')) else None
                    )

                    project_names = clean_project_names(row.get('Нацпроект'))
                    for proj_name in project_names:
                        project_id = await conn.fetchval(
                            'INSERT INTO national_projects (name) VALUES ($1) ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name RETURNING id',
                            proj_name)
                        await conn.execute(
                            'INSERT INTO project_to_goal_mapping (project_id, goal_id) VALUES ($1, $2) ON CONFLICT DO NOTHING',
                            project_id, goal_id)
                        await conn.execute(
                            'INSERT INTO indicator_to_project_mapping (indicator_id, project_id) VALUES ($1, $2) ON CONFLICT DO NOTHING',
                            indicator_id, project_id)

                    for year_col in YEAR_COLUMNS:
                        if year_col in df.columns and pd.notna(row[year_col]):
                            year = int(year_col)
                            value = str(row[year_col])
                            await conn.execute(
                                'INSERT INTO indicator_reference_values (indicator_id, year, reference_value) VALUES ($1, $2, $3) ON CONFLICT (indicator_id, year) DO UPDATE SET reference_value = EXCLUDED.reference_value',
                                indicator_id, year, value)

                    print(f"  -> Успешно обработан индикатор: {indicator_name[:70]}...")

                except Exception as e:
                    print(f"❌ Ошибка при обработке строки {index + 2}: {indicator_name[:70]}... | {e}")

    except Exception as e:
        print(f"🔥 Произошла критическая ошибка: {e}")

    finally:
        if conn:
            await conn.close()
            print("🛑 Соединение с базой данных закрыто.")


if __name__ == "__main__":
    print("🚀 Запуск скрипта для наполнения справочников БД...")
    asyncio.run(main())