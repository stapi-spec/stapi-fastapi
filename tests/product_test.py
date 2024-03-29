from warnings import warn

from fastapi import status
from fastapi.testclient import TestClient
from pytest import fixture

from .utils import find_link
from .warnings import StatSpecWarning


def test_products_response(stat_client: TestClient):
    res = stat_client.get("/products")

    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/json"

    data = res.json()

    assert data["type"] == "ProductCollection"
    assert isinstance(data["products"], list)


@fixture
def product_response(stat_client: TestClient, product_id: str):
    res = stat_client.get(f"/products/{product_id}")

    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/json"

    yield res.json()


def test_product_response_self_link(product_response: dict, product_id: str, url_for):
    link = find_link(product_response["links"], "self")
    if link is None:
        warn(StatSpecWarning("GET /products Link[rel=self] should exist"))
    else:
        assert link["type"] == "application/json"
        assert link["href"] == url_for(f"/products/{product_id}")
