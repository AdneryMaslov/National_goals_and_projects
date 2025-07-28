# app/models/models.py

from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import datetime
from datetime import date

# --- Существующие модели ---

class ParseRequest(BaseModel):
    url: HttpUrl

class ParseResponse(BaseModel):
    message: str
    indicator_name: str
    monthly_rows_added: int
    yearly_rows_added: int

class BudgetSyncResponse(BaseModel):
    message: str
    records_processed: int
    records_added: int
    records_updated: int

class Region(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class Goal(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class Project(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class BudgetItem(BaseModel):
    name: str
    allocated: Optional[float] = None
    executed: Optional[float] = None

class IndicatorData(BaseModel):
    id: int
    name: str
    unit: Optional[str] = None
    region_value: Optional[float] = None
    rf_value: Optional[float] = None
    target_value: Optional[str] = None
    is_reversed: bool

class MetricData(BaseModel):
    name: str
    indicators: List[IndicatorData]

class ProjectParameter(BaseModel):
    name: str
    unit: Optional[str] = None

# ----- ОБНОВЛЕННЫЕ МОДЕЛИ ДЛЯ ГРАФИКА -----

class TimeSeriesDataPoint(BaseModel):
    date: str
    value: float

# Модель для эталонных значений (value может быть текстом)
class ReferenceDataPoint(BaseModel):
    date: str # Год в виде строки
    value: str

class IndicatorHistory(BaseModel):
    yearly_data: List[TimeSeriesDataPoint]
    monthly_data: List[TimeSeriesDataPoint]
    reference_data: List[ReferenceDataPoint] # <-- Добавлено


class ProjectActivity(BaseModel):
    title: str
    activity_date: Optional[datetime.date] = None
    link: Optional[str] = None
    responsible_body: Optional[str] = None
    text: Optional[str] = None
    importance: Optional[int] = None


class ProjectDetails(BaseModel):
    name: str
    budget: List[BudgetItem]
    metrics: List[MetricData]
    activities: List[ProjectActivity]
    parameters: List[ProjectParameter]


class MonthlyBudgetRecord(BaseModel):
    relevance_date: date
    amount_allocated: Optional[float] = None
    amount_executed: Optional[float] = None


class ProjectBudgetHistory(BaseModel):
    region_data: List[MonthlyBudgetRecord]
    rf_data: List[MonthlyBudgetRecord]

class BudgetRecord(BaseModel):
    project_name: str
    region_name: str
    amount_allocated: Optional[float] = None
    amount_executed: Optional[float] = None
    execution_percentage: Optional[float] = None
    relevance_date: date

class NewsSyncResponse(BaseModel):
    message: str
    records_processed: int
    records_added: int
    records_updated: int
