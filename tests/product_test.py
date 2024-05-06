from warnings import warn

from fastapi import status
from fastapi.testclient import TestClient

from stapi_fastapi.models.product import Product
from stapi_fastapi_test_backend.backend import TestBackend

from .utils import find_link
from .warnings import StapiSpecWarning


def test_products_response(stapi_client: TestClient):
    res = stapi_client.get("/products")

    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/json"

    data = res.json()

    assert data["type"] == "ProductCollection"
    assert isinstance(data["products"], list)


def test_product_response_self_link(
    products: list[Product],
    stapi_backend: TestBackend,
    stapi_client: TestClient,
    url_for,
):
    stapi_backend._products = products

    res = stapi_client.get("/products/mock:standard")

    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/json"

    data = res.json()
    link = find_link(data["links"], "self")
    if link is None:
        warn(StapiSpecWarning("GET /products Link[rel=self] should exist"))
    else:
        assert link["type"] == "application/json"
        assert link["href"] == url_for("/products/mock:standard")
