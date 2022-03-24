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


def test_querystring():
    response = requests.get(
        "http://redirect:8080/",
        params={"came_from": "http://example2.com/toto", "test": "toto"},
        allow_redirects=False,
    )
    assert response.status_code == 302, response.text
    assert response.headers["Location"] == "http://example2.com/toto?test=toto"
