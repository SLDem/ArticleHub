import pytest
from unittest.mock import AsyncMock, patch
from app.models.article import Article, ArticleAnalysis
from app.tasks.celery_app import analyze_article_task


@pytest.mark.asyncio
async def test_create_article():
    article = Article(
        title="Test",
        content="Hello world",
        tags=["news", "test"],
        author_id="123"
    )
    await article.insert()
    assert article.id is not None


@pytest.mark.asyncio
async def test_celery_task_creates_analysis():
    # Fake article object
    fake_article = Article(
        id="1",
        title="Fake Article",
        content="Hello world",
        tags=["tag1", "tag2"],
        author_id="123",
        analysis=None
    )
    fake_article.save = AsyncMock(return_value=None)

    # Patch Article.get to return the fake article
    with patch("app.models.article.Article.get", new=AsyncMock(return_value=fake_article)):
        result = analyze_article_task("1")
        assert result == "done"
        assert fake_article.analysis.word_count == len(fake_article.content.split())
        assert fake_article.analysis.unique_tags == len(set(fake_article.tags))