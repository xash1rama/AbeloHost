from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func, select, cast, Date
from datetime import datetime, timedelta
from typing import Optional

from database.DB import Transaction, get_db, AsyncSession
from schemas.schemas import ReportResponse
import logging


logger = logging.getLogger(__name__)

router_report = APIRouter(tags=["Report"])

@router_report.get("/report", response_model=ReportResponse)
async def get_transaction_report(
        start_date: Optional[str] = Query(None, description="Format: YYYY-MM-DD"),
        end_date: Optional[str] = Query(None, description="Format: YYYY-MM-DD"),
        status: str = Query("all", enum=["all", "successful", "failed"]),
        type: str = Query("all", enum=["all", "payment", "invoice"]),
        include_avg: bool = False,
        include_min: bool = False,
        include_max: bool = False,
        include_daily_shift: bool = False,
        db: AsyncSession = Depends(get_db),
):
    logger.info("Start analyze. /report")

    try:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()
        start_dt = (
            datetime.strptime(start_date, "%Y-%m-%d")
            if start_date
            else end_dt - timedelta(days=30)
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    filters = [Transaction.date_payment.between(start_dt, end_dt)]

    if status != "all":
        filters.append(Transaction.status == status)

    if type != "all":
        filters.append(Transaction.type == type)

    metrics_query = select(
        func.sum(Transaction.payment_amount)
        .filter(Transaction.status == "successful")
        .label("total"),
        func.avg(Transaction.payment_amount).label("avg"),
        func.min(Transaction.payment_amount).label("min"),
        func.max(Transaction.payment_amount).label("max"),
        ).where(and_(*filters))

    result = await db.execute(metrics_query)
    stats = result.one()

    report = {
        "total_amount": int(stats.total) if stats.total else 0,
        "avg_amount": float(stats.avg) if include_avg and stats.avg else None,
        "min_amount": int(stats.min) if include_min and stats.min else None,
        "max_amount": int(stats.max) if include_max and stats.max else None,
        "daily_shift": None
    }

    if include_daily_shift:
        daily_query = (
            select(
                cast(Transaction.date_payment, Date).label("day"),
                func.sum(Transaction.payment_amount).label("day_total"),
            )
            .where(and_(*filters))
            .group_by("day")
            .order_by("day")
        )

        daily_res = await db.execute(daily_query)
        rows = daily_res.all()

        daily_data = []
        prev_total = None

        for row in rows:
            change = None
            if prev_total is not None and prev_total > 0:
                change = round(((row.day_total - prev_total) / prev_total) * 100, 2)

            daily_data.append(
                {
                    "date": str(row.day),
                    "total": int(row.day_total),
                    "change_percent": change if change is not None else None,
                }
            )
            prev_total = row.day_total

        report["daily_shift"] = daily_data

    logger.info("Return report analyze.")
    return report
