# Copyright (c) 2022-2026, Camptocamp SA

import httpx
import pytest


@pytest.mark.docker
@pytest.mark.anyio
async def test_docker_app_health():
    async with httpx.AsyncClient(base_url="http://redirect:8080") as client:
        response = await client.get("/")
        assert response.status_code == 400
