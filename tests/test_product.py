import pytest
from fastapi import status
from fastapi.testclient import TestClient

from stapi_fastapi.models.product import Product

from .shared import pagination_tester


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
    assert_link(
        url, body, "create-order", f"/products/{product_id}/orders", method="POST"
    )


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


@pytest.mark.parametrize("limit", [0, 1, 2, 4])
def test_get_products_pagination(
    limit: int,
    stapi_client: TestClient,
    mock_products: list[Product],
):
    expected_returns = []
    if limit != 0:
        for product in mock_products:
            prod = product.model_dump(mode="json", by_alias=True)
            product_id = prod["id"]
            prod["links"] = [
                {
                    "href": f"http://stapiserver/products/{product_id}",
                    "rel": "self",
                    "type": "application/json",
                },
                {
                    "href": f"http://stapiserver/products/{product_id}/constraints",
                    "rel": "constraints",
                    "type": "application/json",
                },
                {
                    "href": f"http://stapiserver/products/{product_id}/order-parameters",
                    "rel": "order-parameters",
                    "type": "application/json",
                },
                {
                    "href": f"http://stapiserver/products/{product_id}/orders",
                    "rel": "create-order",
                    "type": "application/json",
                    "method": "POST",
                },
                {
                    "href": f"http://stapiserver/products/{product_id}/opportunities",
                    "rel": "opportunities",
                    "type": "application/json",
                },
            ]
            expected_returns.append(prod)

    pagination_tester(
        stapi_client=stapi_client,
        url="/products",
        method="GET",
        limit=limit,
        target="products",
        expected_returns=expected_returns,
    )


def test_token_not_found(stapi_client: TestClient) -> None:
    res = stapi_client.get("/products", params={"next": "a_token"})
    assert res.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.mock_products([])
def test_no_products(stapi_client: TestClient):
    res = stapi_client.get("/products")
    body = res.json()
    print("hold")
    assert res.status_code == status.HTTP_200_OK
    assert len(body["products"]) == 0
