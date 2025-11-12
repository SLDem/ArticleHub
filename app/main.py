from fastapi import FastAPI
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.user import User
from app.models.article import Article, ArticleAnalysis
from app.routes import auth, articles
from app.config import settings

app = FastAPI(title="ArticleHub API")

app.include_router(auth.router)
app.include_router(articles.router)

@app.on_event("startup")
async def on_startup():
    client = AsyncIOMotorClient(settings.MONGO_URI)
    await init_beanie(database=client.get_default_database(), document_models=[User, Article])
