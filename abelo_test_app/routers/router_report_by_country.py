from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import pandas as pd
import logging
import os

from database.DB import Transaction, get_db
from schemas.schemas import CountryReportRecord

logger = logging.getLogger(__name__)

router_report_by_country = APIRouter(tags=["Report by country"])

@router_report_by_country.get(
    "/report/by-country",
    response_model=list[CountryReportRecord]
)
async def get_report_by_country(
        sort_by: str = Query("total", enum=["count", "total", "avg"]),
        top_n: Optional[int] = Query(None),
        db: AsyncSession = Depends(get_db),
):
    logger.info(f"Generating country report. Sort: {sort_by}, Top: {top_n}")

    csv_path = "user-country.csv"

    try:
        df_countries = pd.read_csv(csv_path, sep=";")
    except FileNotFoundError:
        logger.error(f"CSV file '{csv_path}' not found!")
        raise HTTPException(status_code=404, detail="Countries data source (CSV) missing")

    query = select(Transaction.user_id, Transaction.payment_amount).where(
        Transaction.status == "successful"
    )
    result = await db.execute(query)

    transactions_data = [row._asdict() for row in result.all()]

    if not transactions_data:
        logger.warning("No successful transactions found in DB.")
        return []

    df_transactions = pd.DataFrame(transactions_data)

    df_merged = pd.merge(df_transactions, df_countries, on="user_id")

    if df_merged.empty:
        logger.warning("Merge resulted in empty DataFrame. Check if IDs in CSV match User IDs in DB.")
        return []

    report_df = (
        df_merged.groupby("country")["payment_amount"]
        .agg(count="count", total="sum", avg="mean")
        .reset_index()
    )

    report_df["avg"] = report_df["avg"].round(2).astype(float)
    report_df["total"] = report_df["total"].astype(int)
    report_df["count"] = report_df["count"].astype(int)

    report_df = report_df.sort_values(by=sort_by, ascending=False)
    if top_n:
        report_df = report_df.head(top_n)

    return report_df.to_dict(orient="records")
