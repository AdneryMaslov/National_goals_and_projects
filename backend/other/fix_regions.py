# ======================================================================================
# ADMIN СКРИПТ ДЛЯ ИСПРАВЛЕНИЯ ДУБЛИКАТОВ В СПРАВОЧНИКАХ
# ======================================================================================

import asyncio
import asyncpg
from dataclasses import dataclass


# --- НАСТРОЙКИ ---
# Заполните данные для подключения к вашей базе данных
# Либо создайте файл .env, как в вашем основном проекте
@dataclass
class DBSettings:
    user: str = "postgres"
    password: str = "mastdmastd"
    host: str = "localhost"
    port: int = 5432
    database: str = "goals_n_projects"

# Названия регионов, которые нужно исправить
INCORRECT_REGION_NAME = "г. Севастополь\\"
CORRECT_REGION_NAME = "г. Севастополь"

# Таблицы, в которых нужно обновить region_id
TABLES_TO_UPDATE = [
    "project_budgets",
    "project_activities",
    "indicator_yearly_values",
    "indicator_monthly_values",
]


async def main():
    """
    Основная функция для выполнения миграции данных.
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

        # Получаем ID для обоих регионов
        correct_region_id = await conn.fetchval("SELECT id FROM regions WHERE name = $1", CORRECT_REGION_NAME)
        incorrect_region_id = await conn.fetchval("SELECT id FROM regions WHERE name = $1", INCORRECT_REGION_NAME)

        if not correct_region_id:
            print(f"❌ ОШИБКА: Корректный регион '{CORRECT_REGION_NAME}' не найден. Прерывание.")
            return
        if not incorrect_region_id:
            print(
                f"🤷‍♂️ ИНФО: Некорректный регион '{INCORRECT_REGION_NAME}' не найден. Возможно, он уже удален. Прерывание.")
            return

        print(
            f"Найдены ID: '{CORRECT_REGION_NAME}' (ID: {correct_region_id}), '{INCORRECT_REGION_NAME}' (ID: {incorrect_region_id})")

        # Начинаем транзакцию
        async with conn.transaction():
            print("\n--- Начало транзакции ---")
            for table in TABLES_TO_UPDATE:
                print(f"\n🔄 Обновление таблицы: {table}...")

                # Сначала получаем все записи, связанные с некорректным ID
                records_to_update = await conn.fetch(f"SELECT * FROM {table} WHERE region_id = $1", incorrect_region_id)

                if not records_to_update:
                    print(f"   В таблице '{table}' нет записей для обновления.")
                    continue

                updated_count = 0
                conflict_count = 0

                for record in records_to_update:
                    # Для каждой записи пытаемся выполнить обновление
                    try:
                        # Уникальный идентификатор записи (обычно 'id')
                        record_id = record['id']
                        await conn.execute(
                            f"UPDATE {table} SET region_id = $1 WHERE id = $2",
                            correct_region_id, record_id
                        )
                        updated_count += 1
                    except asyncpg.UniqueViolationError:
                        # Ловим ошибку дублирования
                        conflict_count += 1
                        print(f"   ⚠️ ПРЕДУПРЕЖДЕНИЕ: Конфликт в таблице '{table}' для записи с id={record['id']}. "
                              f"Запись для региона '{CORRECT_REGION_NAME}' уже существует. Обновление пропущено.")

                print(
                    f"   Обработано записей: {len(records_to_update)}. Успешно обновлено: {updated_count}. Конфликтов: {conflict_count}.")

            # Удаляем некорректную запись из справочника регионов
            print(f"\n🗑️ Удаление некорректного региона '{INCORRECT_REGION_NAME}' (ID: {incorrect_region_id})...")
            await conn.execute("DELETE FROM regions WHERE id = $1", incorrect_region_id)
            print("   Регион успешно удален.")

            print("\n--- Транзакция успешно завершена (зафиксирована) ---")

    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        print("--- Все изменения были отменены (откат транзакции) ---")
    finally:
        if conn:
            await conn.close()
            print("\n🔌 Соединение с базой данных закрыто.")


if __name__ == "__main__":
    print("--- Запуск скрипта для исправления дубликатов регионов ---")
    # ВАЖНО: Перед запуском настоятельно рекомендуется сделать резервную копию базы данных!
    # input("Нажмите Enter для продолжения...")
    asyncio.run(main())

