import asyncpg
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    class Config:
        env_file = ".env"

settings = Settings()
DB_URL = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

db_pool = None

async def get_db_pool():
    return db_pool

async def connect_to_db():
    global db_pool
    print("Подключение к базе данных...")
    try:
        db_pool = await asyncpg.create_pool(DB_URL, min_size=1, max_size=10)
        print("Подключение к базе данных успешно!")
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        db_pool = None

async def close_db_connection():
    global db_pool
    if db_pool:
        print("Закрытие подключения к базе данных...")
        await db_pool.close()
        print("Подключение закрыто.")