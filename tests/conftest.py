import os
from pathlib import Path
from typing import AsyncGenerator, Dict

import pytest
from httpx import AsyncClient
from odmantic.session import AIOSession

from app.core.config import settings
from app.db.session import engine
from app.main import app
from app.testing.user import authentication_token_from_email
from app.testing.utilities import get_superuser_token_headers


@pytest.fixture(scope="session")
def event_loop(request):
    import asyncio
    import logging
    import sys

    """
    Redefine the event loop to support session/module-scoped fixtures;
    see https://github.com/pytest-dev/pytest-asyncio/issues/68

    When running on Windows we need to use a non-default loop for subprocess support.
    """
    if sys.platform == "win32" and sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    policy = asyncio.get_event_loop_policy()

    if sys.version_info < (3, 8) and sys.platform != "win32":
        # Python < 3.8 does not use a `ThreadedChildWatcher` by default which can
        # lead to errors in tests as the previous default `SafeChildWatcher`  is not
        # compatible with threaded event loops.
        raise NotImplementedError

    loop = policy.new_event_loop()

    # configure asyncio logging to capture long running tasks
    asyncio_logger = logging.getLogger("asyncio")
    asyncio_logger.setLevel("WARNING")
    asyncio_logger.addHandler(logging.StreamHandler())
    loop.set_debug(True)
    loop.slow_callback_duration = 0.25

    try:
        yield loop
    finally:
        loop.close()

    # Workaround for failures in pytest_asyncio 0.17;
    # see https://github.com/pytest-dev/pytest-asyncio/issues/257
    policy.set_event_loop(loop)


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
async def db() -> AsyncGenerator[AIOSession, None]:
    async with engine.session() as s:
        assert s.engine.client.address == ("mongo", 27017), "MUST use testing MongoDB"
        yield s


@pytest.fixture(scope="session")
def rootdir() -> Path:
    return Path(os.getcwd())


@pytest.fixture(scope="module")
async def superuser_token_headers(client: AsyncClient) -> Dict[str, str]:
    return await get_superuser_token_headers(client)


@pytest.fixture(scope="module")
async def normal_user_token_headers(
    client: AsyncClient, db: AIOSession
) -> Dict[str, str]:
    return await authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )


@pytest.fixture(scope="module")
async def superuser_id(client: AsyncClient, superuser_token_headers: dict) -> str:
    r = await client.get(
        f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers
    )
    assert r.status_code == 200, r.json()
    current_user = r.json()
    assert current_user["id"]
    return current_user["id"]
