# /backend/pdf_data_extractor.py (ФИНАЛЬНАЯ РАБОЧАЯ ВЕРСИЯ)

import pdfplumber
import pandas as pd
import re
import os

# --- НАСТРОЙКИ ---
PDF_FILE_PATH = "/Users/andrey/Desktop/Наццели 7 шт.pdf"
OUTPUT_EXCEL_PATH = "наццели_результат.xlsx"


def clean_text(text):
    """Убирает лишние пробелы и переносы строк."""
    if not text:
        return ""
    return ' '.join(text.strip().split())


def parse_goals_pdf(file_path: str):
    """
    Основная функция для парсинга PDF-файла с наццелями, показателями и индикаторами.
    """
    if not os.path.exists(file_path):
        print(f"ОШИБКА: Файл не найден по указанному пути: {file_path}")
        return None

    all_indicators = []
    current_goal = "Не определена"
    current_metric = "Не определен"

    print(f"Начинаем обработку файла: {file_path}")

    # Настройки для лучшего распознавания таблиц
    table_settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "text",
        "snap_tolerance": 3,
    }

    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            print(f"--- Обрабатываем страницу {page_num} из {len(pdf.pages)} ---")

            # Извлекаем текст для поиска заголовков
            full_text = page.extract_text(x_tolerance=2, y_tolerance=2) or ""
            lines = full_text.split('\n')

            for line in lines:
                goal_match = re.match(r'^[IVX]+\.\s(.+)', line)
                if goal_match and '...' not in line:
                    current_goal = clean_text(goal_match.group(1))
                    print(f"  [Найдена Наццель]: {current_goal}")
                    current_metric = "Не определен"  # Сбрасываем показатель при смене цели
                    continue

                metric_match = re.match(r'^\d+\.\s(.+)', line)
                if metric_match and '...' not in line:
                    current_metric = clean_text(metric_match.group(1))
                    print(f"    [Найден Показатель]: {current_metric}")

            # Извлекаем таблицы
            tables = page.extract_tables(table_settings)
            if not tables:
                continue

            for table_data in tables:
                if not table_data or len(table_data) < 2:
                    continue

                header = [clean_text(h) for h in table_data[0]]

                # --- ИСПРАВЛЕНИЕ: Ищем любой из правильных заголовков ---
                indicator_col_name = next((h for h in header if 'индикатор' in h.lower()), None)
                unit_col_name = next((h for h in header if 'изм' in h.lower()), None)

                if not indicator_col_name:
                    continue

                print(f"      [Найдена валидная таблица] Заголовок индикатора: '{indicator_col_name}'")

                year_columns = {idx: int(re.search(r'(\d{4})', col).group(1)) for idx, col in enumerate(header) if
                                re.search(r'(\d{4})', col)}
                if not year_columns:
                    continue

                indicator_col_idx = header.index(indicator_col_name)
                unit_col_idx = header.index(unit_col_name) if unit_col_name else -1

                for row in table_data[1:]:
                    if indicator_col_idx >= len(row): continue

                    indicator_name = clean_text(row[indicator_col_idx])
                    if not indicator_name or len(indicator_name) < 5: continue

                    unit = clean_text(row[unit_col_idx]) if unit_col_idx != -1 and row[unit_col_idx] else ''
                    for col_idx, year in year_columns.items():
                        if col_idx < len(row):
                            ref_val_str = (row[col_idx] or "").replace(',', '.')
                            try:
                                ref_val = float(ref_val_str)
                            except (ValueError, TypeError):
                                ref_val = None

                            all_indicators.append({
                                'Национальная цель': current_goal,
                                'Показатель нац. цели': current_metric,
                                'Статистический индикатор': indicator_name,
                                'Единица измерения': unit,
                                'Год': year,
                                'Эталонное значение': ref_val
                            })

    print("\nПарсинг завершен. Создаем DataFrame...")
    df = pd.DataFrame(all_indicators)
    return df


# --- Главный блок для запуска ---
if __name__ == "__main__":
    final_df = parse_goals_pdf(PDF_FILE_PATH)

    if final_df is not None and not final_df.empty:
        try:
            # Сортируем данные для наглядности
            final_df.sort_values(by=['Национальная цель', 'Показатель нац. цели', 'Статистический индикатор', 'Год'],
                                 inplace=True)

            final_df.to_excel(OUTPUT_EXCEL_PATH, index=False, engine='openpyxl')
            print("\n=======================================================")
            print(f"🎉 УСПЕХ! Данные успешно сохранены в файл:")
            print(f"   {os.path.abspath(OUTPUT_EXCEL_PATH)}")
            print("=======================================================")

        except Exception as e:
            print(f"\nОШИБКА: Не удалось сохранить Excel-файл. Причина: {e}")
    else:
        print("\nНе найдено данных для сохранения. Проверьте PDF-файл или логику парсера.")