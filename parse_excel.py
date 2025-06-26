import pandas as pd

source_file = 'C:/Users/droid/Desktop/Сбер/budgets.xlsx'
sheet_to_process = 'Бюджет НП 1q25'
output_file = 'processed_budgets_with_percentage.csv'

try:
    df = pd.read_excel(
        source_file,
        sheet_name=sheet_to_process,
        engine='openpyxl',
        header=[10, 11],
        index_col=0
    )

    df_long = df.stack(level=0, future_stack=True)
    df_tidy = df_long.reset_index()

    index_cols = df_tidy.columns.to_list()[:2]

    df_tidy = df_tidy.rename(columns={
        index_cols[0]: 'Регион',
        index_cols[1]: 'Нацпроект',
        'Назначено, млн руб.': 'Назначено',
        'Исполнено, млн руб.': 'Исполнено',
        '% исполнения': 'Процент исполнения'
    })

    final_columns = ['Регион', 'Нацпроект', 'Назначено', 'Исполнено', 'Процент исполнения']

    if not all(col in df_tidy.columns for col in final_columns):
        print("Критическая ошибка: не удалось найти все ожидаемые столбцы после переименования.")
        print("Пожалуйста, проверьте итоговые столбцы:", df_tidy.columns)
    else:
        df_final = df_tidy[final_columns]

        df_final = df_final.dropna(subset=['Регион', 'Нацпроект'])

        df_final.to_csv(output_file, index=False, encoding='utf-8-sig')

        print(f"Сводная таблица с листа '{sheet_to_process}' успешно преобразована.")
        print(f"Результат сохранен в файл: {output_file}")
        print("\nПервые 10 строк итоговых данных:")
        print(df_final.head(10))

except FileNotFoundError:
    print(f"Ошибка: Файл не найден по пути '{source_file}'.")
except ValueError as e:
    print(f"Ошибка: {e}. Возможно, в файле '{source_file}' нет листа с названием '{sheet_to_process}'.")
except Exception as e:
    print(f"Произошла непредвиденная ошибка: {e}")