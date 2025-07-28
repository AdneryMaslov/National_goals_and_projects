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


def find_filter_id_by_title(config: Dict[str, Any], keywords: list[str]) -> Optional[str]:
    """Ищет ID фильтра по списку возможных ключевых слов."""
    for filter_id, filter_data in config.get("filters", {}).items():
        title_lower = filter_data.get("title", "").lower()
        for keyword in keywords:
            if keyword.lower() in title_lower:
                return filter_id
    return None


async def fetch_all_indicator_data(client: httpx.AsyncClient, indicator_id: int, config: Dict[str, Any],
                                   source_url: str) -> Optional[Dict[str, Any]]:
    """Автоматически определяет все измерения для строк и столбцов и формирует payload."""
    region_filter_id = find_filter_id_by_title(config, ["территори", "окато", "оксм"])
    period_filter_id = find_filter_id_by_title(config, ["период"])
    year_filter_id = find_filter_id_by_title(config, ["год"])

    if not region_filter_id:
        print("Критическая ошибка: Не удалось найти ID для регионального измерения.")
        return None

    column_ids = {fid for fid in [year_filter_id, period_filter_id] if fid}
    line_ids = [fid for fid in config.get("filters", {}).keys() if fid not in column_ids]

    payload = {
        'id': str(indicator_id),
        'lineObjectIds': line_ids,
        'columnObjectIds': list(column_ids),
        'selectedFilterIds': []
    }

    for filter_id, filter_data in config.get("filters", {}).items():
        for value_id in filter_data.get("values", {}).keys():
            payload['selectedFilterIds'].append(f"{filter_id}_{value_id}")

    try:
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': source_url}
        response = await client.post(DATA_API_URL, data=payload, headers=headers, timeout=45.0)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        print(f"Ошибка запроса к API данных: {e}")
        return None


def process_api_response(api_data: Dict[str, Any], config: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """ФИНАЛЬНАЯ ВЕРСИЯ: Обрабатывает все известные структуры ответа API."""
    region_filter_id = find_filter_id_by_title(config, ["территори", "окато", "оксм"])
    period_filter_id = find_filter_id_by_title(config, ["период"])

    if not region_filter_id: return pd.DataFrame(), pd.DataFrame()

    try:
        period_map = {}
        if period_filter_id:
            period_map = {k: v['title'].strip() for k, v in config['filters'][period_filter_id]['values'].items()}
        region_dim_key = f"dim{region_filter_id}"
    except KeyError as e:
        print(f"Ошибка в структуре конфигурации: {e}")
        return pd.DataFrame(), pd.DataFrame()

    all_rows = []
    for result_row in api_data.get("results", []):
        region_name = result_row.get(region_dim_key)
        if not region_name: continue

        for key, value in result_row.items():
            if not key.startswith("dim"): continue

            parts = key[3:].split('_')
            year, period_name = None, None

            # --- НАЧАЛО УНИВЕРСАЛЬНОЙ ЛОГИКИ ---
            # Сценарий 1: ключ = dim<ГОД> (например, для 40466)
            if len(parts) == 1 and parts[0].isdigit():
                year, period_name = int(parts[0]), "значение показателя за год"

            elif len(parts) > 1:
                # Сценарий 2: ключ = dim<ГОД>_<ID_ПЕРИОДА>... (для 62083)
                if parts[0].isdigit() and len(parts[0]) == 4 and parts[1] in period_map:
                    year, period_name = int(parts[0]), period_map.get(parts[1])
                # Сценарий 3: ключ = dim<ID_ПЕРИОДА>_<ГОД>... (для 59263)
                elif parts[1].isdigit() and len(parts[1]) == 4 and parts[0] in period_map:
                    year, period_name = int(parts[1]), period_map.get(parts[0])
            # --- КОНЕЦ УНИВЕРСАЛЬНОЙ ЛОГИКИ ---

            if year and period_name:
                all_rows.append({
                    "region_name": region_name, "year": year,
                    "period_name": period_name,
                    "measured_value": str(value).replace(',', '.') if value is not None else None
                })

    if not all_rows: return pd.DataFrame(), pd.DataFrame()

    df = pd.DataFrame(all_rows)
    df = df[pd.to_numeric(df['measured_value'], errors='coerce').notna()]
    df['measured_value'] = pd.to_numeric(df['measured_value'])

    yearly_df = df[df['period_name'].str.contains('значение показателя за год', case=False, na=False)].copy()
    yearly_df.drop_duplicates(subset=['region_name', 'year'], keep='first', inplace=True)
    yearly_df.rename(columns={'measured_value': 'yearly_value'}, inplace=True)

    def get_month_from_period(p_name):
        p_lower = p_name.lower()
        if 'декабрь' in p_lower: return 12
        if 'ноябрь' in p_lower: return 11
        if 'октябрь' in p_lower: return 10
        if 'сентябрь' in p_lower: return 9
        if 'август' in p_lower: return 8
        if 'июль' in p_lower: return 7
        if 'июнь' in p_lower: return 6
        if 'май' in p_lower: return 5
        if 'апрель' in p_lower: return 4
        if 'март' in p_lower: return 3
        if 'февраль' in p_lower: return 2
        if 'январь' in p_lower: return 1
        return None

    df['month'] = df['period_name'].apply(get_month_from_period)
    monthly_df = df.dropna(subset=['month']).copy()

    if not monthly_df.empty:
        monthly_df['month'] = monthly_df['month'].astype(int)
        monthly_df.drop_duplicates(subset=['region_name', 'year', 'month'], keep='first', inplace=True)
        monthly_df['value_date'] = pd.to_datetime({'year': monthly_df['year'], 'month': monthly_df['month'], 'day': 1},
                                                  errors='coerce')
        monthly_df.dropna(subset=['value_date'], inplace=True)
        return monthly_df[['region_name', 'value_date', 'measured_value']], yearly_df[
            ['region_name', 'year', 'yearly_value']]

    return pd.DataFrame(), yearly_df[['region_name', 'year', 'yearly_value']]


async def get_indicator_data_from_url(url: str):
    """Главная функция, которая управляет сессией и выполняет все запросы."""
    indicator_id_match = re.search(r"/indicator/(\d+)", url)
    if not indicator_id_match: return None, None, None
    indicator_id = int(indicator_id_match.group(1))

    async with httpx.AsyncClient() as client:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = await client.get(url, headers=headers, follow_redirects=True, timeout=20.0)
            response.raise_for_status()
            html_content = response.text
        except httpx.RequestError as e:
            print(f"Ошибка получения HTML страницы: {e}")
            return None, None, None

        config = extract_grid_config(html_content)
        if not config: return None, None, None

        print("Конфигурация получена. Запрашиваем все данные одним запросом...")
        api_data = await fetch_all_indicator_data(client, indicator_id, config, url)
        if not api_data: return None, None, None

        print(f"Получено {len(api_data.get('results', []))} строк от API. Обрабатываем...")
        monthly_df, yearly_df = process_api_response(api_data, config)

    metadata = {'name': config.get('title', ''), 'unit': config.get('unit', '')}
    return metadata, monthly_df, yearly_df