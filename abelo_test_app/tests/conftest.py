import pytest
import asyncio
from httpx import AsyncClient
from abelo_test_app.main import app
from abelo_test_app.database.DB import Base, engine

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    # Создаем таблицы перед тестами
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Удаляем после (опционально)
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def aclient():
    async with AsyncClient(app=app, base_url="http://test") as aclient:
        yield aclient