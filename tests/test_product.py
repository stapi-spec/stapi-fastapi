import pytest
from fastapi import status
from fastapi.testclient import TestClient


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
    assert_link,
):
    res = stapi_client.get(f"/products/{product_id}")
    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/json"

    body = res.json()

    url = "GET /products"
    assert_link(url, body, "self", f"/products/{product_id}")
    assert_link(url, body, "constraints", f"/products/{product_id}/constraints")
    assert_link(
        url, body, "order-parameters", f"/products/{product_id}/order-parameters"
    )
    assert_link(url, body, "opportunities", f"/products/{product_id}/opportunities")
    assert_link(url, body, "create-order", f"/products/{product_id}/orders")


@pytest.mark.parametrize("product_id", ["test-spotlight"])
def test_product_constraints_response(
    product_id: str,
    stapi_client: TestClient,
):
    res = stapi_client.get(f"/products/{product_id}/constraints")
    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/json"

    json_schema = res.json()
    assert "properties" in json_schema
    assert "off_nadir" in json_schema["properties"]


@pytest.mark.parametrize("product_id", ["test-spotlight"])
def test_product_order_parameters_response(
    product_id: str,
    stapi_client: TestClient,
):
    res = stapi_client.get(f"/products/{product_id}/order-parameters")
    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/json"

    json_schema = res.json()
    assert "properties" in json_schema
    assert "s3_path" in json_schema["properties"]


@pytest.mark.parametrize("limit", [1])
def test_product_pagination(stapi_client: TestClient, limit: int):
    res = stapi_client.get("/products", params={"next": None, "limit": limit})
    assert res.status_code == status.HTTP_200_OK
    body = res.json()
    assert len(body["products"]) == limit
    links = body["links"]
    for d in body["links"]:
        if ("rel", "next") in d.items():
            next = d["href"]

    while len(links) > 1:
        res = stapi_client.get(next)
        assert res.status_code == status.HTTP_200_OK
        body = res.json()
        assert body["products"] != []
        links = body["links"]
        for d in body["links"]:
            if ("rel", "next") in d.items():
                assert len(body["products"]) == limit
                next = body["links"][0]["href"]


def test_token_not_found(stapi_client: TestClient) -> None:
    res = stapi_client.get("/products", params={"next": "a_token"})
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_no_products(empty_stapi_client: TestClient):
    res = empty_stapi_client.get("/products")
    body = res.json()
    print("hold")
    assert res.status_code == status.HTTP_200_OK
    assert len(body["products"]) == 0
