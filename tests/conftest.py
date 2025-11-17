import pytest
from httpx import AsyncClient
from app.main import app
from app.articles.models import init_beanie_db, Article
import asyncio
from httpx._transports.asgi import ASGITransport

@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


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
    await Article.get_pymongo_collection().delete_many({})


@pytest.fixture(scope="session", autouse=True)
def test_user():
    return  {
      "id": "64f09b",
      "email": "user@example.com",
      "name": "John Doe"
    }


@pytest.fixture(scope="session", autouse=True)
def test_article():
    return {
        "id": "6502ac",
        "title": "My test article",
        "content": "Some test",
        "tags": ["python", "test"],
        "author": "64f09b",
        "created_at": "2025-08-30T18:00:00Z",
        "analysis": {
            "word_count": 2,
            "unique_tags": 2
        }
    }
