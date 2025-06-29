# /app/api/endpoints.py
from fastapi import APIRouter, HTTPException
from app.models.models import ParseRequest, ParseResponse
from app.services.parser import get_indicator_data_from_url
from app.services.db_manager import save_parsed_data

router = APIRouter()


@router.post("/process-indicator/", response_model=ParseResponse)
async def process_indicator_endpoint(request: ParseRequest):
    url_str = str(request.url)
    print(f"--- Начинаем обработку: {url_str} ---")

    metadata, monthly_df, yearly_df = await get_indicator_data_from_url(url_str)

    if metadata is None or not metadata.get('name'):
        raise HTTPException(status_code=500, detail="Не удалось спарсить данные.")

    print(f"Спарсены метаданные для: '{metadata['name']}'")

    try:
        monthly_count, yearly_count = await save_parsed_data(metadata, monthly_df, yearly_df)
    except Exception as e:
        print(f"Критическая ошибка при сохранении в БД: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения в БД: {str(e)}")

    return ParseResponse(
        message="Данные успешно спарсены и сохранены",
        indicator_name=metadata['name'],
        monthly_rows_added=len(monthly_df) if monthly_df is not None else 0,
        yearly_rows_added=len(yearly_df) if yearly_df is not None else 0
    )