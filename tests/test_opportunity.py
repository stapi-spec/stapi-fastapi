import pytest
from fastapi.testclient import TestClient

from stapi_fastapi.models.opportunity import (
    OpportunityCollection,
)

from .shared import create_mock_opportunity, pagination_tester


def test_search_opportunities_response(
    stapi_client: TestClient, assert_link, opportunity_search
) -> None:
    product_id = "test-spotlight"
    url = f"/products/{product_id}/opportunities"

    response = stapi_client.post(url, json=opportunity_search)

    assert response.status_code == 200, f"Failed for product: {product_id}"
    body = response.json()

    # Validate the opportunity was returned
    assert len(body["features"]) == 1

    try:
        _ = OpportunityCollection(**body)
    except Exception as _:
        pytest.fail("response is not an opportunity collection")

    assert_link(
        f"POST {url}",
        body,
        "create-order",
        f"/products/{product_id}/orders",
        method="POST",
    )


@pytest.mark.parametrize("limit", [0, 1, 2, 4])
def test_search_opportunities_pagination(
    limit: int,
    stapi_client: TestClient,
    opportunity_search,
) -> None:
    mock_pagination_opportunities = [create_mock_opportunity() for __ in range(3)]
    stapi_client.app_state["_opportunities"] = mock_pagination_opportunities
    product_id = "test-spotlight"
    expected_returns = []
    if limit != 0:
        expected_returns = [
            x.model_dump(mode="json") for x in mock_pagination_opportunities
        ]

    pagination_tester(
        stapi_client=stapi_client,
        url=f"/products/{product_id}/opportunities",
        method="POST",
        limit=limit,
        target="features",
        expected_returns=expected_returns,
        body=opportunity_search,
    )
