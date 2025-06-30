import httpx
import json
import re
import pandas as pd
from typing import Dict, Any, Tuple, Optional

DATA_API_URL = "https://fedstat.ru/indicator/dataGrid.do"


def extract_grid_config(html_content: str) -> Optional[Dict[str, Any]]:
    """Извлекает и очищает объект конфигурации FGrid из HTML-кода."""
    match = re.search(r"new FGrid\((.*?)\);", html_content, re.DOTALL)
    if not match:
        print("Ошибка: Конфигурация FGrid не найдена на странице.")
        return None

    config_str = match.group(1).strip()
    try:
        config_str = re.sub(r"block\s*:\s*\$\('#grid'\),?", "", config_str)
        config_str = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', config_str)
        config_str = config_str.replace("'", '"')
        config_str = re.sub(r',\s*([}\]])', r'\1', config_str)
        return json.loads(config_str)
    except json.JSONDecodeError as e:
        print(f"Критическая ошибка декодирования JSON: {e}")
        return None


async def fetch_all_indicator_data(client: httpx.AsyncClient, indicator_id: int, config: Dict[str, Any],
                                   source_url: str) -> Optional[Dict[str, Any]]:
    """
    Формирует правильный payload в виде словаря со списками и отправляет
    ЕДИНСТВЕННЫЙ POST-запрос для получения данных.
    """
    # --- НОВЫЙ, БОЛЕЕ НАДЕЖНЫЙ СПОСОБ ФОРМИРОВАНИЯ PAYLOAD ---
    payload = {
        'id': str(indicator_id),
        'lineObjectIds': ['0', '30611', '36175'],
        'columnObjectIds': ['3', '33560'],
        'selectedFilterIds': []  # Создаем пустой список
    }

    # Динамически наполняем список selectedFilterIds
    for filter_id, filter_data in config.get("filters", {}).items():
        for value_id in filter_data.get("values", {}).keys():
            payload['selectedFilterIds'].append(f"{filter_id}_{value_id}")
    # -----------------------------------------------------------

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Referer': source_url
        }
        # httpx сам правильно закодирует словарь со списками в нужный формат
        response = await client.post(DATA_API_URL, data=payload, headers=headers, timeout=45.0)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        print(f"Ошибка запроса к API данных: {e}")
        return None


def process_api_response(api_data: Dict[str, Any], config: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Обрабатывает единый JSON-ответ от API и превращает его в два DataFrame."""
    try:
        region_map = {k: v['title'].strip() for k, v in config['filters']['36175']['values'].items()}
        period_map = {k: v['title'].strip() for k, v in config['filters']['33560']['values'].items()}
    except KeyError as e:
        print(f"Ошибка: Не найден ключ фильтра в конфигурации: {e}")
        return pd.DataFrame(), pd.DataFrame()

    all_rows = []
    for result_row in api_data.get("results", []):
        region_name = result_row.get("dim36175")
        for key, value in result_row.items():
            if key.startswith("dim") and "_" in key:
                parts = key.split('_')
                if len(parts) >= 2:
                    year, period_id = parts[0][3:], parts[1]
                    all_rows.append({
                        "region_name": region_name, "year": int(year),
                        "period_name": period_map.get(period_id, "Неизвестный период"),
                        "measured_value": str(value).replace(',', '.') if value is not None else None
                    })

    if not all_rows: return pd.DataFrame(), pd.DataFrame()

    df = pd.DataFrame(all_rows)
    df = df[pd.to_numeric(df['measured_value'], errors='coerce').notna()]
    df['measured_value'] = pd.to_numeric(df['measured_value'])

    # --- Обработка годовых данных ---
    yearly_df = df[df['period_name'] == 'значение показателя за год'].copy()
    yearly_df.drop_duplicates(subset=['region_name', 'year'], keep='first', inplace=True)
    yearly_df.rename(columns={'measured_value': 'yearly_value'}, inplace=True)

    # --- Обработка месячных данных ---
    month_map = {
        'январь': 1, 'январь-февраль': 2, 'январь-март': 3, 'январь-апрель': 4,
        'январь-май': 5, 'январь-июнь': 6, 'январь-июль': 7, 'январь-август': 8,
        'январь-сентябрь': 9, 'январь-октябрь': 10, 'январь-ноябрь': 11, 'январь-декабрь': 12,
        'январь-январь': 1  # Оставляем дубликат для маппинга
    }
    monthly_df = df[df['period_name'].isin(month_map.keys())].copy()

    if not monthly_df.empty:
        monthly_df['month'] = monthly_df['period_name'].map(month_map)

        # --- КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ ---
        # Удаляем дубликаты, которые могли возникнуть для одного и того же месяца
        # (например, из-за 'январь' и 'январь-январь')
        monthly_df.drop_duplicates(subset=['region_name', 'year', 'month'], keep='first', inplace=True)
        # ---------------------------

        monthly_df['value_date'] = pd.to_datetime(
            {'year': monthly_df['year'], 'month': monthly_df['month'], 'day': 1},
            errors='coerce'
        )
        monthly_df.dropna(subset=['value_date'], inplace=True)

        return monthly_df[['region_name', 'value_date', 'measured_value']], yearly_df[
            ['region_name', 'year', 'yearly_value']]

    return pd.DataFrame(), yearly_df[['region_name', 'year', 'yearly_value']]


async def get_indicator_data_from_url(url: str):
    """Главная функция, которая управляет сессией и выполняет все запросы."""
    indicator_id_match = re.search(r"/indicator/(\d+)", url)
    if not indicator_id_match: return None, None, None
    indicator_id = int(indicator_id_match.group(1))

    # --- ИЗМЕНЕНИЕ №2: Создаем ОДИН клиент и используем его для всех запросов ---
    async with httpx.AsyncClient() as client:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            # Шаг 1: Получаем HTML и cookies
            response = await client.get(url, headers=headers, follow_redirects=True, timeout=20.0)
            response.raise_for_status()
            html_content = response.text
        except httpx.RequestError as e:
            print(f"Ошибка получения HTML страницы: {e}")
            return None, None, None

        config = extract_grid_config(html_content)
        if not config: return None, None, None

        print("Конфигурация получена. Запрашиваем все данные одним запросом...")
        # Шаг 2: Передаем уже существующий 'client' в функцию запроса данных
        api_data = await fetch_all_indicator_data(client, indicator_id, config, url)
        if not api_data: return None, None, None

        print(f"Получено {len(api_data.get('results', []))} строк от API. Обрабатываем...")
        monthly_df, yearly_df = process_api_response(api_data, config)

    metadata = {'name': config.get('title', ''), 'unit': config.get('unit', '')}
    return metadata, monthly_df, yearly_df