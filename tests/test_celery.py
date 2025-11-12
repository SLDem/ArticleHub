import pytest
from app.tasks.celery_app import analyze_article_task
from app.models.article import Article

@pytest.mark.asyncio
async def test_celery_task_creates_analysis():
    article = Article(
        title="Celery Test",
        content="This is celery test content",
        tags=["celery"],
        author_id="321"
    )
    await article.insert()

    result = analyze_article_task(article.id)
    assert result == "done"

    updated = await Article.get(article.id)
    assert updated.analysis.word_count == len(article.content.split())
    assert updated.analysis.unique_tags == len(set(article.tags))
