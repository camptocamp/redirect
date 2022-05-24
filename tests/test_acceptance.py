import requests


def test_test1():
    response = requests.get(
        "http://redirect:8080/", params={"came_from": "http://example1.com/toto"}, allow_redirects=False
    )
    assert response.status_code == 302, response.text
    assert response.headers["Location"] == "http://example1.com/toto"


def test_test2():
    response = requests.get(
        "http://redirect:8080/", params={"came_from": "http://example2.com/toto"}, allow_redirects=False
    )
    assert response.status_code == 302, response.text
    assert response.headers["Location"] == "http://example2.com/toto"


def test_params():
    response = requests.get(
        "http://redirect:8080/",
        params={"came_from": "http://example2.com/toto?p1=1", "p2": "2"},
        allow_redirects=False,
    )
    assert response.status_code == 302, response.text
    assert response.headers["Location"] == "http://example2.com/toto?p1=1&p2=2"


def test_params_same():
    response = requests.get(
        "http://redirect:8080/",
        params={"came_from": "http://example2.com/toto?p1=1", "p1": "2"},
        allow_redirects=False,
    )
    assert response.status_code == 302, response.text
    assert response.headers["Location"] == "http://example2.com/toto?p1=2"


def test_test_other():
    response = requests.get(
        "http://redirect:8080/", params={"came_from": "http://example3.com/toto"}, allow_redirects=False
    )
    assert response.status_code == 400, response.text


def test_wrong():
    response = requests.get(
        "http://redirect:8080/", params={"came_from2": "http://example2.com/toto"}, allow_redirects=False
    )
    assert response.status_code == 400, response.text


def test_error():
    response = requests.get("http://redirect:8080/", params={"error": "An error."}, allow_redirects=False)
    assert response.status_code == 400, response.text
    assert response.text == "\n".join(
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
        )
    )


def test_querystring():
    response = requests.get(
        "http://redirect:8080/",
        params={"came_from": "http://example2.com/toto", "test": "toto"},
        allow_redirects=False,
    )
    assert response.status_code == 302, response.text
    assert response.headers["Location"] == "http://example2.com/toto?test=toto"
