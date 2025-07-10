import pandas as pd

# --- НАСТРОЙКИ ---
# Имя вашего исходного файла
INPUT_FILE = 'table_csv.csv'
# Имя файла, в который будет сохранен результат
OUTPUT_FILE = 'table_csv_1.csv'
# Название столбца, который нужно обработать
COLUMN_TO_CLEAN = 'Статистический индикатор'


def clean_name(indicator_name: str) -> str:
    """
    Принимает название индикатора и отсекает единицу измерения,
    которая обычно идет после последней запятой.
    """
    if not isinstance(indicator_name, str):
        return ""

    # Находим позицию последней запятой
    last_comma_index = indicator_name.rfind(',')

    # Если запятая найдена, возвращаем часть строки до нее
    if last_comma_index != -1:
        return indicator_name[:last_comma_index].strip()

    # Если запятой нет, возвращаем исходную строку без изменений
    return indicator_name.strip()


def main():
    """
    Главная функция для чтения, обработки и сохранения файла.
    """
    try:
        # Читаем исходный CSV-файл, используя точку с запятой как разделитель
        print(f"📖 Чтение исходного файла: {INPUT_FILE}...")
        df = pd.read_csv(INPUT_FILE, engine='python', sep=';')
        print("✅ Файл успешно прочитан.")

        # Применяем нашу функцию очистки к нужному столбцу
        print(f"🧹 Очистка столбца '{COLUMN_TO_CLEAN}'...")
        df[COLUMN_TO_CLEAN] = df[COLUMN_TO_CLEAN].apply(clean_name)
        print("✅ Столбец успешно очищен.")

        # Сохраняем результат в новый файл
        print(f"💾 Сохранение результата в файл: {OUTPUT_FILE}...")
        df.to_csv(OUTPUT_FILE, sep=';', index=False, encoding='utf-8')
        print(f"🎉 Готово! Очищенные данные сохранены в {OUTPUT_FILE}.")

    except FileNotFoundError:
        print(f"🔥 ОШИБКА: Файл '{INPUT_FILE}' не найден. Убедитесь, что он находится в той же папке, что и скрипт.")
    except Exception as e:
        print(f"🔥 Произошла непредвиденная ошибка: {e}")


if __name__ == "__main__":
    main()
