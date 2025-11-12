import pytest
from httpx import AsyncClient
from app.main import app
from app.models.article import init_beanie_db, Article
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(app=app, base_url="http://testserver") as c:
        yield c

@pytest.fixture(scope="function", autouse=True)
async def init_db():
    await init_beanie_db()
    yield
    await Article.get_motor_collection().delete_many({})
