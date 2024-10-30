import json
from warnings import warn

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from .utils import find_link
from .warnings import StapiSpecWarning


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
    print(json.dumps(res.json(), indent=4))
    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/json"

    data = res.json()
    link = find_link(data["links"], "self")
    if link is None:
        warn(StapiSpecWarning("GET /products Link[rel=self] should exist"))
    else:
        assert link["type"] == "application/json"
        assert link["href"] == url_for(f"/products/{product_id}")
