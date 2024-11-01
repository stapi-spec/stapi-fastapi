from fastapi import status
from fastapi.testclient import TestClient

from .utils import find_link


def test_root(stapi_client: TestClient, url_for) -> None:
    res = stapi_client.get("/")

    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/json"

    data = res.json()

    link = find_link(data["links"], "self")
    assert link, "GET / Link[rel=self] should exist"
    assert link["type"] == "application/json"
    assert link["href"] == url_for("/")

    link = find_link(data["links"], "service-description")
    assert link, "GET / Link[rel=service-description] should exist"
    assert link["type"] == "application/json"
    assert str(link["href"]) == url_for("/openapi.json")

    link = find_link(data["links"], "service-docs")
    assert link, "GET / Link[rel=service-docs] should exist"
    assert link["type"] == "text/html"
    assert str(link["href"]) == url_for("/docs")
