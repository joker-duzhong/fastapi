from typing import Dict

from httpx import AsyncClient

from app.core.config import settings


async def test_get_access_token(client: AsyncClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = await client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert r.status_code == 200, r.json()
    tokens = r.json()
    assert "access_token" in tokens
    assert tokens["access_token"]


async def test_use_access_token(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    r = await client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200, r.json()
    result = r.json()
    assert "email" in result
