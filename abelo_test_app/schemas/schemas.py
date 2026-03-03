from pydantic import BaseModel

class DailyMetric(BaseModel):
    date: str
    total: int
    change_percent: None|float

class ReportResponse(BaseModel):
    total_amount: int
    avg_amount: None|float
    min_amount: None|int
    max_amount: None|int
    daily_shift: None|list[DailyMetric]