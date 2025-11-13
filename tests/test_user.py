import pytest
from unittest.mock import AsyncMock, patch
from app.tasks.celery_app import analyze_article_task


@pytest.mark.asyncio
async def test_user_registration(test_user):
    user = test_user
    with patch("app.models.user.User.get", new=AsyncMock(return_value=user)):
        result = analyze_article_task("1")
        assert result == "done"
        assert user.analysis.word_count == len(user.content.split())
        assert user.analysis.unique_tags == len(set(user.tags))
