import pytest


@pytest.mark.anyio
async def test_test1(client):
    response = await client.get(
        "/",
        params={"came_from": "http://example1.com/toto"},
    )
    assert response.status_code == 302, response.text
    assert response.headers["location"] == "http://example1.com/toto"


@pytest.mark.anyio
async def test_test2(client):
    response = await client.get(
        "/",
        params={"came_from": "http://example2.com/toto"},
    )
    assert response.status_code == 302, response.text
    assert response.headers["location"] == "http://example2.com/toto"


@pytest.mark.anyio
async def test_params(client):
    response = await client.get(
        "/",
        params={"came_from": "http://example2.com/toto?p1=1", "p2": "2"},
    )
    assert response.status_code == 302, response.text
    assert response.headers["location"] == "http://example2.com/toto?p1=1&p2=2"


@pytest.mark.anyio
async def test_params_same(client):
    response = await client.get(
        "/",
        params={"came_from": "http://example2.com/toto?p1=1", "p1": "2"},
    )
    assert response.status_code == 302, response.text
    assert response.headers["location"] == "http://example2.com/toto?p1=2"


@pytest.mark.anyio
async def test_test_other(client):
    response = await client.get(
        "/",
        params={"came_from": "http://example3.com/toto"},
    )
    assert response.status_code == 400, response.text


@pytest.mark.anyio
async def test_wrong(client):
    response = await client.get(
        "/",
        params={"came_from2": "http://example2.com/toto"},
    )
    assert response.status_code == 400, response.text


@pytest.mark.anyio
async def test_error(client):
    response = await client.get("/", params={"error": "An error."})
    assert response.status_code == 400, response.text
    assert response.text == "\n".join(  # noqa: FLY002
        (
            "<html>",
            " <head>",
            "  <title>400 Bad Request</title>",
            " </head>",
            " <body>",
            "  <h1>400 Bad Request</h1>",
            "  The server could not comply with the request since it is either malformed or otherwise incorrect.<br/><br/>",
            "Missing &#x27;came_from&#x27; parameter<br/>",
            "<br/>",
            "error: An error.",
            " </body>",
            "</html>",
        ),
    )


@pytest.mark.anyio
async def test_querystring(client):
    response = await client.get(
        "/",
        params={"came_from": "http://example2.com/toto", "test": "toto"},
    )
    assert response.status_code == 302, response.text
    assert response.headers["location"] == "http://example2.com/toto?test=toto"
