import pytest
from unittest.mock import AsyncMock, patch
from app.tasks.celery_app import analyze_article_task


@pytest.mark.asyncio
async def test_celery_task_creates_analysis(test_article):
    article = test_article
    with patch("app.models.article.Article.get", new=AsyncMock(return_value=article)):
        result = analyze_article_task("1")
        assert result == "done"
        assert article.analysis.word_count == len(article.content.split())
        assert article.analysis.unique_tags == len(set(article.tags))
