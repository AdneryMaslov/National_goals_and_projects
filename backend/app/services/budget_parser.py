# app/services/budget_parser.py
import httpx
from typing import List, Dict, Any


async def fetch_budget_data(url: str) -> List[Dict[str, Any]]:
    """
    Получает данные о бюджетах из удаленного API.

    Args:
        url: URL-адрес для получения данных.

    Returns:
        Список словарей, где каждый словарь представляет одну запись о бюджете.

    Raises:
        httpx.RequestError: Если происходит ошибка сети.
        ValueError: Если ответ не является валидным JSON.
    """
    print(f"Запрашиваем данные о бюджетах с: {url}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()  # Вызовет исключение для кодов 4xx/5xx
            data = response.json()
            print(f"Успешно получено {len(data)} записей.")
            return data
        except httpx.HTTPStatusError as e:
            print(f"Ошибка статуса HTTP: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            print(f"Произошла ошибка при получении данных о бюджетах: {e}")
            raise
