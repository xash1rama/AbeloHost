import os

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from main import app, get_db

from dotenv import load_dotenv

load_dotenv()
DB_NAME_TEST = os.getenv("DB_NAME_TEST")


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

test_engine = create_async_engine(DB_NAME_TEST, echo=False)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)

async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        from database.DB import Base
        await conn.run_sync(Base.metadata.create_all)
    yield