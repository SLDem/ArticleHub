from app.articles.models import init_beanie_db, Article, ArticleAnalysis
import asyncio
from celery.signals import worker_process_init
from .celery_app import celery_app


@worker_process_init.connect
def init_worker(**kwargs):
    # Windows only
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_beanie_db())


@celery_app.task
def send_welcome_email(user_id: str, email: str):
    async def run():
        print(f"Sending welcome email to {email} (user id: {user_id})")

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(run())

@celery_app.task
def analyze_article_task(article_id: str):
    async def run():
        article = await Article.get(article_id)
        if not article:
            return "not found"

        word_count = len(article.content.split())
        unique_tags = len(set(article.tags))
        article.analysis = ArticleAnalysis(word_count=word_count, unique_tags=unique_tags)
        await article.save()
        return "done"

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(run())
