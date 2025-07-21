import asyncpg
from pydantic_settings import BaseSettings
import asyncio # Импортируем asyncio для организации пауз

class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    class Config:
        env_file = (".env", "../.env")
        env_file_encoding = 'utf-8'

settings = Settings()

DB_URL = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

db_pool = None

async def get_db_pool():
    return db_pool

async def connect_to_db():
    """
    Подключается к базе данных с несколькими попытками.
    Это необходимо для стабильной работы в Docker, где бэкенд может запуститься
    раньше, чем база данных будет готова принимать подключения.
    """
    global db_pool
    attempts = 5
    for i in range(attempts):
        print(f"Подключение к базе данных... (Попытка {i + 1}/{attempts})")
        try:
            # Пытаемся создать пул соединений
            db_pool = await asyncpg.create_pool(DB_URL, min_size=1, max_size=10, timeout=5)
            print("✅ Подключение к базе данных успешно!")
            return # Выходим из функции при успехе
        except Exception as e:
            # --- ИЗМЕНЕНИЕ ЗДЕСЬ: Исправлена опечатка с 'fa' на 'f' ---
            print(f"⚠️ Ошибка подключения к БД: {e}")
            if i < attempts - 1:
                print("   Повторная попытка через 3 секунды...")
                await asyncio.sleep(3) # Ждем 3 секунды перед следующей попыткой
            else:
                print("❌ Не удалось подключиться к базе данных после нескольких попыток.")
                db_pool = None

async def close_db_connection():
    global db_pool
    if db_pool:
        print("Закрытие подключения к базе данных...")
        await db_pool.close()
        print("Подключение закрыто.")
