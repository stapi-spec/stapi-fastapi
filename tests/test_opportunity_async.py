import pytest
from fastapi.testclient import TestClient

from stapi_fastapi.models.opportunity import (
    OpportunityCollection,
    OpportunitySearchRecord,
)

from .shared import (
    product_test_spotlight,
    product_test_spotlight_async_opportunity,
    product_test_spotlight_sync_async_opportunity,
)


@pytest.mark.parametrize("mock_products", [[product_test_spotlight]])
def test_no_opportunity_search(
    stapi_client: TestClient, assert_link, mock_products
) -> None:
    # TODO: Add checks for root async links
    product_id = "test-spotlight"
    response = stapi_client.get(f"/products/{product_id}")

    body = response.json()
    url = "GET /products"

    with pytest.raises(AssertionError, match=".*should exist"):
        assert_link(url, body, "opportunities", f"/products/{product_id}/opportunities")


# handled in test_opportunity.py
def test_sync_search() -> None:
    pass


@pytest.mark.parametrize("mock_products", [[product_test_spotlight_async_opportunity]])
def test_async_search_response(
    stapi_client_async_opportunity: TestClient,
    assert_link,
    opportunity_search,
    mock_products,
) -> None:
    product_id = "test-spotlight"
    url = f"/products/{product_id}/opportunities"

    response = stapi_client_async_opportunity.post(url, json=opportunity_search)

    assert response.status_code == 201, f"Failed for product: {product_id}"
    body = response.json()

    try:
        _ = OpportunitySearchRecord(**body)
    except Exception as _:
        pytest.fail("response is not an opportunity search record")

    assert_link(
        f"GET /searches/opportunities/{body['id']}",
        body,
        "self",
        f"/searches/opportunities/{body['id']}",
        media_type="application/json",
    )


@pytest.mark.parametrize(
    "mock_products", [[product_test_spotlight_sync_async_opportunity]]
)
def test_async_search_is_default(
    stapi_client_async_opportunity: TestClient,
    assert_link,
    mock_products,
    opportunity_search,
) -> None:
    product_id = "test-spotlight"
    url = f"/products/{product_id}/opportunities"

    response = stapi_client_async_opportunity.post(url, json=opportunity_search)

    assert response.status_code == 201, f"Failed for product: {product_id}"
    body = response.json()

    try:
        _ = OpportunitySearchRecord(**body)
    except Exception as _:
        pytest.fail("response is not an opportunity search record")


@pytest.mark.parametrize(
    "mock_products", [[product_test_spotlight_sync_async_opportunity]]
)
def test_prefer_header(
    stapi_client_async_opportunity: TestClient,
    assert_link,
    mock_products,
    opportunity_search,
) -> None:
    product_id = "test-spotlight"
    url = f"/products/{product_id}/opportunities"

    # prefer = "wait"
    response = stapi_client_async_opportunity.post(
        url, json=opportunity_search, headers={"Prefer": "wait"}
    )

    assert response.status_code == 200, f"Failed for product: {product_id}"
    assert response.headers["Preference-Applied"] == "wait"
    body = response.json()

    try:
        OpportunityCollection(**body)
    except Exception as _:
        pytest.fail("response is not an opportunity collection")

    # prefer = "respond-async"
    response = stapi_client_async_opportunity.post(
        url, json=opportunity_search, headers={"Prefer": "respond-async"}
    )

    assert response.status_code == 201, f"Failed for product: {product_id}"
    assert response.headers["Preference-Applied"] == "respond-async"
    body = response.json()

    try:
        OpportunitySearchRecord(**body)
    except Exception as _:
        pytest.fail("response is not an opportunity search record")


# test than after an async request we can get the search record by id and that it exists
# in the list returned from the searches/opportunities endpoint.


# test that we can get the completed opportunity collection from the
# /products/{product_id}/opportunities//{oppportunity_collection_id} endpoint


# will need some pagination testing in here


# there's a location header to check for
