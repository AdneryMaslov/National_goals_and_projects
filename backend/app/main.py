# app/main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import connect_to_db, close_db_connection
from app.api.endpoints import router as api_router
from fastapi.middleware.cors import CORSMiddleware # 1. Импортируйте middleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_db()
    yield
    await close_db_connection()

app = FastAPI(
    title="Сервис анализа национальных целей",
    description="MVP для парсинга и сохранения данных с Fedstat",
    version="0.1.0",
    lifespan=lifespan
)

# --- 2. ДОБАВЬТЕ ЭТОТ БЛОК КОДА ---
# Настройка CORS: разрешаем нашему фронтенду делать запросы к бэкенду
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ВАЖНО: для реального проекта здесь должен быть адрес вашего фронтенда, например ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы (GET, POST и т.д.)
    allow_headers=["*"],  # Разрешаем все заголовки
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Сервис запущен. Для доступа к API перейдите на /docs"}