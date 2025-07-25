# app/api/endpoints.py

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from tabulate import tabulate
import datetime
import pandas as pd

from app.models.models import (
    Region, Goal, Project, ProjectDetails, BudgetItem, MetricData, IndicatorData, ProjectParameter,
    ParseRequest, ParseResponse, IndicatorHistory, TimeSeriesDataPoint, ReferenceDataPoint, ProjectActivity,
    BudgetSyncResponse, ProjectBudgetHistory
)
from app.core.database import get_db_pool
from app.services.parser import get_indicator_data_from_url
from app.services.db_manager import save_parsed_data
from app.services.budget_parser import fetch_budget_data
from app.services.db_manager import save_parsed_data, save_budget_data

router = APIRouter()


@router.post("/process-indicator/", response_model=ParseResponse, tags=["Parser"])
async def process_indicator_endpoint(request: ParseRequest):
    url_str = str(request.url)
    print(f"--- Начинаем обработку: {url_str} ---")

    metadata, monthly_df, yearly_df = await get_indicator_data_from_url(url_str)

    if metadata is None or not metadata.get('name'):
        raise HTTPException(status_code=500, detail="Не удалось спарсить данные.")

    print(f"Спарсены метаданные для: '{metadata['name']}'")

    # -- Заглушка для проверки парсера --
    monthly_rows_count = len(monthly_df) if monthly_df is not None else 0
    yearly_rows_count = len(yearly_df) if yearly_df is not None else 0

    print("\n--- РЕЗУЛЬТАТЫ ПАРСИНГА (без сохранения в БД) ---")

    if yearly_rows_count > 0:
        print("\n[+] Годовые данные:")
        # Выводим первые 5 строк для предпросмотра
        print(tabulate(yearly_df.head(), headers='keys', tablefmt='psql'))
        if yearly_rows_count > 5:
            print(f"... и еще {yearly_rows_count - 5} строк.")
    else:
        print("\n[-] Годовые данные не найдены.")

    if monthly_rows_count > 0:
        print("\n[+] Месячные данные:")
        # Выводим первые 5 строк для предпросмотра
        print(tabulate(monthly_df.head(), headers='keys', tablefmt='psql'))
        if monthly_rows_count > 5:
            print(f"... и еще {monthly_rows_count - 5} строк.")
    else:
        print("\n[-] Месячные данные не найдены.")

    print("\n--- Конец результатов ---")

    # --- Возвращаем сохранение в БД ---
    # try:
    #     await save_parsed_data(
    #         metadata=metadata,
    #         monthly_df=monthly_df,
    #         yearly_df=yearly_df
    #     )
    # except Exception as e:
    #     # Ловим и выводим как ошибки парсинга, так и ошибки сохранения
    #     print(f"Критическая ошибка: {e}")
    #     raise HTTPException(status_code=500, detail=f"Ошибка обработки или сохранения: {str(e)}")

    return ParseResponse(
        message="Данные успешно спарсены и сохранены",
        indicator_name=metadata['name'],
        monthly_rows_added=len(monthly_df) if monthly_df is not None else 0,
        yearly_rows_added=len(yearly_df) if yearly_df is not None else 0
    )


@router.post("/budgets/sync", response_model=BudgetSyncResponse, tags=["Parser"])
async def sync_budgets():
    """
    Запускает процесс получения и сохранения данных о бюджетах национальных проектов.
    """
    budget_data_url = "https://parser-project-urfu.ru/parsers/iminfin/project-data/"

    try:
        # Шаг 1: Получаем данные
        data = await fetch_budget_data(budget_data_url)
        if not data:
            raise HTTPException(status_code=404, detail="Данные о бюджетах не найдены по указанному URL.")

        # --- ИЗМЕНЕНИЕ ЗДЕСЬ: Возвращаем сохранение в БД ---

        # Шаг 2: Сохранение данных в БД
        added, updated = await save_budget_data(data)

        return BudgetSyncResponse(
            message="Синхронизация бюджетов успешно завершена.",
            records_processed=len(data),
            records_added=added,
            records_updated=updated
        )

    except Exception as e:
        print(f"Критическая ошибка во время синхронизации бюджетов: {e}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

#---------------------------------------------------------------------------------------

@router.get("/regions", response_model=List[Region], tags=["Data"])
async def get_all_regions():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        records = await conn.fetch("SELECT id, name FROM regions ORDER BY name")
        return [dict(record) for record in records]


@router.get("/goals", response_model=List[Goal], tags=["Data"])
async def get_all_goals():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        records = await conn.fetch("SELECT id, name FROM national_goals ORDER BY id")
        return [dict(record) for record in records]


@router.get("/goals/{goal_id}/projects", response_model=List[Project], tags=["Data"])
async def get_projects_for_goal(goal_id: int):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        query = """
            SELECT p.id, p.name 
            FROM national_projects p
            JOIN project_to_goal_mapping pgm ON p.id = pgm.project_id
            WHERE pgm.goal_id = $1
            ORDER BY p.name;
        """
        records = await conn.fetch(query, goal_id)
        return [dict(record) for record in records]


@router.get("/data", response_model=ProjectDetails, tags=["Data"])
async def get_final_data(
        region_id: int,
        goal_id: int,
        project_id: int,
        year: int = Query(default=2024, description="Год для выборки данных")
):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        project_record = await conn.fetchrow("SELECT name FROM national_projects WHERE id = $1", project_id)
        if not project_record:
            raise HTTPException(status_code=404, detail="Проект не найден")

        budget_data_list = []

        # Находим ID для Российской Федерации
        rf_region_record = await conn.fetchrow("SELECT id, name FROM regions WHERE name ILIKE 'Российская Федерация'")

        # --- Логика получения бюджетов (остается без изменений) ---
        if rf_region_record:
            rf_budget_record = await conn.fetchrow(
                """
                SELECT SUM(amount_allocated) as allocated, SUM(amount_executed) as executed 
                FROM project_budgets 
                WHERE project_id = $1 AND region_id = $2 AND EXTRACT(YEAR FROM relevance_date) = $3
                """,
                project_id, rf_region_record['id'], year
            )
            if rf_budget_record and rf_budget_record['allocated'] is not None:
                budget_data_list.append(BudgetItem(name=rf_region_record['name'], **dict(rf_budget_record)))

        if not rf_region_record or region_id != rf_region_record['id']:
            region_record = await conn.fetchrow("SELECT name FROM regions WHERE id = $1", region_id)
            if region_record:
                budget_record = await conn.fetchrow(
                    """
                    SELECT SUM(amount_allocated) as allocated, SUM(amount_executed) as executed 
                    FROM project_budgets 
                    WHERE project_id = $1 AND region_id = $2 AND EXTRACT(YEAR FROM relevance_date) = $3
                    """,
                    project_id, region_id, year
                )
                if budget_record and budget_record['allocated'] is not None:
                    budget_data_list.append(BudgetItem(name=region_record['name'], **dict(budget_record)))

        # --- ИЗМЕНЕНИЕ ЗДЕСЬ: Логика получения новостей в зависимости от региона ---

        # Определяем, является ли выбранный регион "Российская Федерация"
        is_rf_selected = rf_region_record and region_id == rf_region_record['id']

        if is_rf_selected:
            # Если выбрана РФ, показываем новости со всех регионов для данного проекта
            activities_query = """
                SELECT title, activity_date, link, responsible_body, text, importance
                FROM project_activities
                WHERE project_id = $1
                ORDER BY activity_date DESC NULLS LAST;
            """
            activity_records = await conn.fetch(activities_query, project_id)
        else:
            # Иначе, показываем новости только для выбранного региона
            activities_query = """
                SELECT title, activity_date, link, responsible_body, text, importance
                FROM project_activities
                WHERE project_id = $1 AND region_id = $2
                ORDER BY activity_date DESC NULLS LAST;
            """
            activity_records = await conn.fetch(activities_query, project_id, region_id)

        activities = [ProjectActivity(**dict(rec)) for rec in activity_records]

        # --- КОНЕЦ ИЗМЕНЕНИЙ ---

        parameter_records = await conn.fetch(
            "SELECT name, unit FROM project_parameters WHERE project_id = $1 ORDER BY id", project_id)
        parameters = [ProjectParameter(**dict(rec)) for rec in parameter_records]

        indicators_query = """
            SELECT
                gm.id AS metric_id,
                gm.name AS metric_name,
                i.id AS indicator_id,
                i.name AS indicator_name,
                i.unit,
                i.desired_direction,
                iv.yearly_value AS region_value,
                irv.reference_value AS target_value,
                (SELECT AVG(iv_rf.yearly_value) FROM indicator_yearly_values iv_rf WHERE iv_rf.indicator_id = i.id AND iv_rf.year = $3) AS rf_value
            FROM indicators i
            JOIN goal_metrics gm ON i.metric_id = gm.id
            JOIN indicator_to_project_mapping itpm ON i.id = itpm.indicator_id
            LEFT JOIN indicator_yearly_values iv ON i.id = iv.indicator_id AND iv.region_id = $1 AND iv.year = $3
            LEFT JOIN indicator_reference_values irv ON i.id = irv.indicator_id AND irv.year = $3
            WHERE 
                gm.goal_id = $2 
                AND itpm.project_id = $4
            ORDER BY gm.id, i.id;
        """
        indicator_rows = await conn.fetch(indicators_query, region_id, goal_id, year, project_id)

        metrics_dict = {}
        for row in indicator_rows:
            metric_id = row['metric_id']
            if metric_id not in metrics_dict:
                metrics_dict[metric_id] = MetricData(name=row['metric_name'], indicators=[])

            metrics_dict[metric_id].indicators.append(
                IndicatorData(
                    id=row['indicator_id'],
                    name=row['indicator_name'],
                    unit=row['unit'],
                    region_value=row['region_value'],
                    rf_value=row['rf_value'],
                    target_value=row['target_value'],
                    is_reversed=(row['desired_direction'] == 'lower')
                )
            )

        return ProjectDetails(
            name=project_record['name'],
            budget=budget_data_list,
            metrics=list(metrics_dict.values()),
            activities=activities,
            parameters=parameters
        )


@router.get("/budgets/history", response_model=ProjectBudgetHistory, tags=["Data"])
async def get_budget_history(project_id: int, region_id: int, year: int):
    """
    Возвращает помесячную историю исполнения бюджета для выбранного проекта и региона
    за указанный год, а также данные по РФ для сравнения.
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Получаем ID РФ
        rf_region_record = await conn.fetchrow("SELECT id FROM regions WHERE name ILIKE 'Российская Федерация'")
        rf_region_id = rf_region_record['id'] if rf_region_record else -1

        # Запрос для получения данных
        query = """
            SELECT relevance_date, amount_allocated, amount_executed
            FROM project_budgets
            WHERE project_id = $1 AND region_id = $2 AND EXTRACT(YEAR FROM relevance_date) = $3
            ORDER BY relevance_date;
        """

        # Получаем данные для выбранного региона
        region_records = await conn.fetch(query, project_id, region_id, year)

        # Получаем данные для РФ
        rf_records = []
        if rf_region_id != -1:
            rf_records = await conn.fetch(query, project_id, rf_region_id, year)

        return ProjectBudgetHistory(
            region_data=[dict(rec) for rec in region_records],
            rf_data=[dict(rec) for rec in rf_records]
        )


@router.get("/indicator/{indicator_id}/history", response_model=IndicatorHistory, tags=["Data"])
async def get_indicator_history(indicator_id: int, region_id: int):
    """
    Возвращает годовую, месячную и эталонную историю значений для
    конкретного индикатора и региона для построения графика.
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Запрос годовых данных
        yearly_query = """
            SELECT year::text as date, yearly_value as value
            FROM indicator_yearly_values
            WHERE indicator_id = $1 AND region_id = $2
            ORDER BY year;
        """
        yearly_records = await conn.fetch(yearly_query, indicator_id, region_id)

        # Запрос месячных данных
        monthly_query = """
            SELECT to_char(value_date, 'YYYY-MM-DD') as date, measured_value as value
            FROM indicator_monthly_values
            WHERE indicator_id = $1 AND region_id = $2
            ORDER BY value_date;
        """
        monthly_records = await conn.fetch(monthly_query, indicator_id, region_id)

        # НОВЫЙ ЗАПРОС: Получаем эталонные значения
        reference_query = """
            SELECT year::text as date, reference_value as value
            FROM indicator_reference_values
            WHERE indicator_id = $1
            ORDER BY year;
        """
        reference_records = await conn.fetch(reference_query, indicator_id)

        return IndicatorHistory(
            yearly_data=[TimeSeriesDataPoint(**dict(rec)) for rec in yearly_records],
            monthly_data=[TimeSeriesDataPoint(**dict(rec)) for rec in monthly_records],
            reference_data=[ReferenceDataPoint(**dict(rec)) for rec in reference_records]
        )
