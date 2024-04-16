from warnings import warn

from fastapi import status
from fastapi.testclient import TestClient

from stat_fastapi.models.product import Product
from stat_fastapi_test_backend.backend import TestBackend

from .utils import find_link
from .warnings import StatSpecWarning


def test_products_response(stat_client: TestClient):
    res = stat_client.get("/products")

    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/json"

    data = res.json()

    assert data["type"] == "ProductCollection"
    assert isinstance(data["products"], list)


def test_product_response_self_link(
    products: list[Product], stat_backend: TestBackend, stat_client: TestClient, url_for
):
    stat_backend._products = products

    res = stat_client.get("/products/mock:standard")

    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/json"

    data = res.json()
    link = find_link(data["links"], "self")
    if link is None:
        warn(StatSpecWarning("GET /products Link[rel=self] should exist"))
    else:
        assert link["type"] == "application/json"
        assert link["href"] == url_for("/products/mock:standard")
