# diagnostic_parser.py

import asyncio
import httpx
import json
import re
import pandas as pd
from typing import Dict, Any, Tuple, Optional

# --- Копируем все функции из вашего app/services/parser.py ---

DATA_API_URL = "https://fedstat.ru/indicator/dataGrid.do"


def extract_grid_config(html_content: str) -> Optional[Dict[str, Any]]:
    match = re.search(r"new FGrid\((.*?)\);", html_content, re.DOTALL)
    if not match: return None
    config_str = match.group(1).strip()
    try:
        config_str = re.sub(r"block\s*:\s*\$\('#grid'\),?", "", config_str)
        config_str = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', config_str)
        config_str = config_str.replace("'", '"')
        config_str = re.sub(r',\s*([}\]])', r'\1', config_str)
        return json.loads(config_str)
    except json.JSONDecodeError:
        return None


async def fetch_all_indicator_data(indicator_id: int, config: Dict[str, Any], source_url: str) -> Optional[
    Dict[str, Any]]:
    payload = {"id": str(indicator_id)}
    for filter_id, filter_data in config.get("filters", {}).items():
        value_ids = list(filter_data.get("values", {}).keys())
        payload[f"filter_{filter_id}"] = value_ids

    try:
        async with httpx.AsyncClient() as client:
            await client.get(source_url, headers={'User-Agent': 'Mozilla/5.0'})
            headers = {'User-Agent': 'Mozilla/5.0', 'Referer': source_url}
            response = await client.post(DATA_API_URL, data=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        print(f"Ошибка запроса к API данных: {e}")
        return None


def process_api_response(api_data: Dict[str, Any], config: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame]:
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

    df = pd.DataFrame(all_rows).drop_duplicates()
    df = df[pd.to_numeric(df['measured_value'], errors='coerce').notna()]
    df['measured_value'] = pd.to_numeric(df['measured_value'])

    yearly_df = df[df['period_name'] == 'значение показателя за год'].rename(
        columns={'measured_value': 'yearly_value'})[['region_name', 'year', 'yearly_value']]

    month_map = {'январь': 1, 'январь-февраль': 2, 'январь-март': 3, 'январь-апрель': 4, 'январь-май': 5,
                 'январь-июнь': 6, 'январь-июль': 7, 'январь-август': 8, 'январь-сентябрь': 9, 'январь-октябрь': 10,
                 'январь-ноябрь': 11, 'январь-декабрь': 12, 'январь-январь': 1}
    monthly_df = df[df['period_name'].isin(month_map.keys())].copy()
    if not monthly_df.empty:
        monthly_df['month'] = monthly_df['period_name'].map(month_map)
        monthly_df['value_date'] = pd.to_datetime({'year': monthly_df['year'], 'month': monthly_df['month'], 'day': 1},
                                                  errors='coerce')

    return monthly_df[['region_name', 'value_date', 'measured_value']], yearly_df


# --- Главная диагностическая функция ---
async def run_diagnostic(url: str):
    print(f"--- Запускаем диагностику для URL: {url} ---")

    indicator_id_match = re.search(r"/indicator/(\d+)", url)
    if not indicator_id_match:
        print("ОШИБКА: Не удалось извлечь ID индикатора из URL")
        return
    indicator_id = int(indicator_id_match.group(1))

    try:
        async with httpx.AsyncClient() as client:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = await client.get(url, headers=headers, follow_redirects=True, timeout=20.0)
            response.raise_for_status()
        html_content = response.text
        print("Шаг 1: HTML страницы успешно получен.")
    except httpx.RequestError as e:
        print(f"ОШИБКА на Шаге 1: {e}")
        return

    config = extract_grid_config(html_content)
    if not config:
        print("ОШИБКА: Не удалось извлечь конфигурацию.")
        return
    print("Шаг 2: Конфигурация успешно извлечена.")

    api_data = await fetch_all_indicator_data(indicator_id, config, url)
    if not api_data:
        print("ОШИБКА: Не удалось получить данные от API.")
        return
    print("Шаг 3: Данные от API успешно получены.")

    # Сохраняем ответ для ручной проверки
    with open('api_response_diagnostic.json', 'w', encoding='utf-8') as f:
        json.dump(api_data, f, ensure_ascii=False, indent=2)
    print("Полный ответ от API сохранен в 'api_response_diagnostic.json'")

    monthly_df, yearly_df = process_api_response(api_data, config)
    print("Шаг 4: Данные обработаны в DataFrame.")

    # --- САМАЯ ВАЖНАЯ ЧАСТЬ ДИАГНОСТИКИ ---
    print("\n" + "=" * 20 + " РЕЗУЛЬТАТ ДИАГНОСТИКИ " + "=" * 20)
    if not monthly_df.empty:
        print("--- Месячные данные ---")
        print("Распределение записей по годам:")
        print(monthly_df['value_date'].dt.year.value_counts())
        print(f"\nОбщее количество месячных строк: {len(monthly_df)}")
    else:
        print("Месячные данные не найдены.")

    if not yearly_df.empty:
        print("\n--- Годовые данные ---")
        print("Распределение записей по годам:")
        print(yearly_df['year'].value_counts())
    else:
        print("\nГодовые данные не найдены.")


if __name__ == "__main__":
    test_url = "https://fedstat.ru/indicator/62083"
    asyncio.run(run_diagnostic(test_url))