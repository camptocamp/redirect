# Copyright (c) 2022-2026, Camptocamp SA

import os
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

os.environ["REDIRECT__REDIRECT_HOSTS"] = str(Path(__file__).parent / "hosts.yaml")

from redirect import app  # noqa: E402


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://redirect:8080",
    ) as client:
        yield client
