import pytest
from fastapi import status
from fastapi.testclient import TestClient

from .utils import find_link


def test_products_response(stapi_client: TestClient):
    res = stapi_client.get("/products")

    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/json"

    data = res.json()

    assert data["type"] == "ProductCollection"
    assert isinstance(data["products"], list)


@pytest.mark.parametrize("product_id", ["test-spotlight"])
def test_product_response_self_link(
    product_id: str,
    stapi_client: TestClient,
    url_for,
):
    res = stapi_client.get(f"/products/{product_id}")
    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/json"

    data = res.json()
    link = find_link(data["links"], "self")
    assert link, "GET /products Link[rel=self] should exist"
    assert link["type"] == "application/json"
    assert link["href"] == url_for(f"/products/{product_id}")


@pytest.mark.parametrize("product_id", ["test-spotlight"])
def test_product_constraints_response(
    product_id: str,
    stapi_client: TestClient,
):
    res = stapi_client.get(f"/products/{product_id}/constraints")
    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/json"

    data = res.json()
    assert "properties" in data
    assert "datetime" in data["properties"]
    assert "off_nadir" in data["properties"]
