from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from typing import Optional

from abelo_test_app.database.DB import Transaction, get_db, AsyncSession
from abelo_test_app.schemas.schemas import CountryReportRecord

import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)



router_report_by_country = APIRouter(tags=["Report by country"])

@router_report_by_country.get("/report/by-country", response_model=list[CountryReportRecord])
async def get_report_by_country(
        sort_by: str = Query("total", enum=["count", "total", "avg"]),
        top_n: Optional[int] = Query(None),
        db: AsyncSession = Depends(get_db)
):
    logger.info(f"Generating country report. Sort: {sort_by}, Top: {top_n}")

    try:
        df_countries = pd.read_csv("user-country.csv")
    except FileNotFoundError:
        logger.error("CSV file 'user-country.csv' not found!")
        return {"error": "CSV file not found"}

    query = select(Transaction.user_id, Transaction.payment_amount).where(Transaction.status == "successful")
    result = await db.execute(query)

    transactions_data = [dict(row._mapping) for row in result.all()]
    df_transactions = pd.DataFrame(transactions_data)

    if df_transactions.empty:
        logger.warning("No successful transactions found in DB.")
        return []

    df_merged = pd.merge(df_transactions, df_countries, on="user_id")

    if df_merged.empty:
        logger.warning("Merge resulted in empty DataFrame (user_id mismatch).")
        return []

    report_df = df_merged.groupby("country")["payment_amount"].agg(
        count="count",
        total="sum",
        avg="mean"
    ).reset_index()

    report_df = report_df.sort_values(by=sort_by, ascending=False)

    if top_n:
        report_df = report_df.head(top_n)

    logger.info(f"Report generated successfully. Countries processed: {len(report_df)}")
    return report_df.to_dict(orient="records")