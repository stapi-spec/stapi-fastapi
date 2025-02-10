from fastapi import status
from fastapi.testclient import TestClient

from stapi_fastapi.models.conformance import CORE


def test_root(stapi_client: TestClient, assert_link) -> None:
    res = stapi_client.get("/")

    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/json"

    body = res.json()

    assert body["conformsTo"] == [CORE]

    assert_link("GET /", body, "self", "/")
    assert_link("GET /", body, "service-description", "/openapi.json")
    assert_link("GET /", body, "service-docs", "/docs", media_type="text/html")
    assert_link("GET /", body, "conformance", "/conformance")
    assert_link("GET /", body, "products", "/products")
    assert_link("GET /", body, "orders", "/orders", media_type="application/geo+json")
