import asyncio
from beanie import Document, init_beanie
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


class ArticleAnalysis(BaseModel):  # embedded document
    word_count: int = 0
    unique_tags: int = 0


class Article(Document):
    title: str
    content: str
    tags: List[str] = []
    author_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    analysis: Optional[ArticleAnalysis] = None

    class Settings:
        name = "articles"

    # sync wrapper for Celery
    @staticmethod
    def get_sync(article_id: str):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(Article.get(article_id))
        loop.close()
        return result

    def save_sync(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.save())
        loop.close()


async def init_beanie_db():
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client.get_default_database()
    await init_beanie(database=db, document_models=[Article])