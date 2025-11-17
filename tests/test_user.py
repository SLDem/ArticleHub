import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_user_registration():
    payload = {
        "email": "test@example.com",
        "password": "strongpass",
        "name": "John Doe"
    }

    fake_user = AsyncMock()
    fake_user.id = "fakeid"
    fake_user.email = payload["email"]
    fake_user.name = payload["name"]

    async_mock_find = AsyncMock(return_value=None)

    with patch("app.auth.router.User", return_value=fake_user), \
         patch("app.auth.router.User.find_one", new=async_mock_find), \
         patch("app.auth.router.send_welcome_email.delay") as mock_celery:

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            response = await ac.post("/api/auth/register/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["name"] == payload["name"]
    assert data["id"] == "fakeid"
    mock_celery.assert_called_once()
    fake_user.insert.assert_awaited_once()
