from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import connect_to_db, close_db_connection
from app.api.endpoints import router as api_router

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

# Подключаем роутер с нашими эндпоинтами
app.include_router(api_router, prefix="/api", tags=["Parser"])

@app.get("/")
def read_root():
    return {"message": "Сервис запущен. Для доступа к API перейдите на /docs"}