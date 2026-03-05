import asyncio
import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import select, func
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database.DB import get_db, User, Transaction, engine, Base
import logging
from time import time


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

fake = Faker()


@asynccontextmanager
async def lifespan(app: FastAPI):
    connected = False
    for i in range(20):
        try:
            async with engine.begin() as conn:
                await conn.execute(select(1))
                await conn.run_sync(Base.metadata.create_all)
            connected = True
            break
        except Exception: ##ДАДА я знаю)
            logger.warning(f"⏳ DB loading... (try {i+1}/20)...")
            await asyncio.sleep(2)

    if not connected:
        return

    async for session in get_db():
        logger.info("Checking database for existing test data...")
        examination = await session.execute(select(func.count(User.id)))
        exam_user_count = examination.scalar()

        if exam_user_count == 0:
            logger.info("Database is empty. Starting generation of 100 users...")
            users = []
            for _ in range(100):
                new_user = User(
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=fake.unique.email(),
                    date_registration=datetime.now()
                    - timedelta(
                        days=random.randint(0, 730), hours=random.randint(0, 23)
                    ),
                )
                users.append(new_user)

            session.add_all(users)
            await session.flush()

            user_ids = [usr.id for usr in users]
            logger.info(
                f"Successfully created 100 users. Starting transactions generation..."
            )

            for idx in range(10):
                new_transactions = []
                for _ in range(1000):
                    new_transaction = Transaction(
                        status=random.choice(["successful", "failed"]),
                        payment_amount=random.randint(1, 1000),
                        type=random.choice(["payment", "invoice"]),
                        date_payment=datetime.now()
                        - timedelta(
                            days=random.randint(0, 730),
                            hours=random.randint(0, 23),
                        ),
                        user_id=random.choice(user_ids),
                    )
                    new_transactions.append(new_transaction)

                session.add_all(new_transactions)
                await session.commit()
                logger.info(f"Batch {idx+1}/10: 1000 transactions committed.")

            logger.info("All test data successfully created!")
        else:
            logger.info("Database already has data. Skipping generation.")

    yield
