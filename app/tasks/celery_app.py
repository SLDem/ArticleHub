from celery import Celery
import asyncio
from app.models.article import init_beanie_db, Article, ArticleAnalysis
from app.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)
celery_app.autodiscover_tasks(["app.tasks"])


import asyncio
from celery import Celery
from celery.signals import worker_process_init
from app.models.article import init_beanie_db, Article, ArticleAnalysis
from app.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)
celery_app.autodiscover_tasks(["app.tasks"])


@worker_process_init.connect
def init_worker(**kwargs):
    # Windows only
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

    # Use the current loop in this worker process
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_beanie_db())


@celery_app.task
def send_welcome_email(user_id: str, email: str):
    print(f"Sending welcome email to {email} (user id: {user_id})")


@celery_app.task
def analyze_article_task(article_id: str):
    """
    Celery task running async Beanie calls in the *worker's loop*, no new loop.
    """
    async def run():
        article = await Article.get(article_id)
        if not article:
            return "not found"

        word_count = len(article.content.split())
        unique_tags = len(set(article.tags))
        article.analysis = ArticleAnalysis(word_count=word_count, unique_tags=unique_tags)
        await article.save()
        return "done"

    # Get the already initialized loop
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(run())
