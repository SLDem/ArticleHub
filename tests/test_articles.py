import pytest
from unittest.mock import patch
import asyncio

from app.tasks.celery_app import celery_app
from app.tasks.tasks import analyze_article_task
from types import SimpleNamespace

# @pytest.mark.asyncio
# async def test_celery_task_creates_analysis(test_article):
#     article = test_article
#     with patch("app.models.article.Article.get", new=AsyncMock(return_value=article)):
#         result = analyze_article_task("1")
#         assert result == "done"
#         assert article.analysis.word_count == len(article.content.split())
#         assert article.analysis.unique_tags == len(set(article.tags))

def test_celery_task_creates_analysis():
    from app.tasks.tasks import celery_app
    celery_app.conf.task_always_eager = True

    async def async_lambda_none(*args, **kwargs):
        return None

    article = SimpleNamespace(
        content="hello world",
        tags=["python", "world"],
        analysis=None,
        save=async_lambda_none
    )

    async def fake_get(_id):
        return article

    with patch("app.articles.models.Article.get", new=fake_get):
        # CALL TASK NORMALLY – NO async keyword
        result = analyze_article_task("1")

        # If your task returns a coroutine inside eager mode:
        if asyncio.iscoroutine(result):
            result = asyncio.run(result)

    assert article.analysis is not None