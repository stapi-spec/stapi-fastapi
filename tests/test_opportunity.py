from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from stapi_fastapi.models.opportunity import (
    OpportunityCollection,
)

from .shared import create_mock_opportunity, pagination_tester
from .test_datetime_interval import rfc3339_strftime


@pytest.mark.parametrize("product_id", ["test-spotlight"])
def test_search_opportunities_response(
    product_id: str,
    stapi_client: TestClient,
    assert_link,
) -> None:
    now = datetime.now(UTC)
    end = now + timedelta(days=5)
    format = "%Y-%m-%dT%H:%M:%S.%f%z"
    start_string = rfc3339_strftime(now, format)
    end_string = rfc3339_strftime(end, format)

    request_payload = {
        "search": {
            "geometry": {
                "type": "Point",
                "coordinates": [0, 0],
            },
            "datetime": f"{start_string}/{end_string}",
            "filter": {
                "op": "and",
                "args": [
                    {"op": ">", "args": [{"property": "off_nadir"}, 0]},
                    {"op": "<", "args": [{"property": "off_nadir"}, 45]},
                ],
            },
        },
        "limit": 10,
    }

    url = f"/products/{product_id}/opportunities"

    response = stapi_client.post(url, json=request_payload)

    assert response.status_code == 200, f"Failed for product: {product_id}"
    body = response.json()

    # Validate the opportunity was returned
    assert len(body["features"]) == 1

    try:
        _ = OpportunityCollection(**body)
    except Exception as _:
        pytest.fail("response is not an opportunity collection")

    assert_link(f"POST {url}", body, "create-order", f"/products/{product_id}/orders")


@pytest.mark.parametrize("limit", [0, 1, 2, 4])
def test_search_opportunities_pagination(
    limit: int,
    stapi_client: TestClient,
) -> None:
    mock_pagination_opportunities = [create_mock_opportunity() for __ in range(3)]
    stapi_client.app_state["_opportunities"] = mock_pagination_opportunities
    product_id = "test-spotlight"
    expected_returns = []
    if limit != 0:
        expected_returns = [
            x.model_dump(mode="json") for x in mock_pagination_opportunities
        ]

    now = datetime.now(UTC)
    start = now
    end = start + timedelta(days=5)
    format = "%Y-%m-%dT%H:%M:%S.%f%z"
    start_string = rfc3339_strftime(start, format)
    end_string = rfc3339_strftime(end, format)

    request_payload = {
        "geometry": {
            "type": "Point",
            "coordinates": [0, 0],
        },
        "datetime": f"{start_string}/{end_string}",
        "filter": {
            "op": "and",
            "args": [
                {"op": ">", "args": [{"property": "off_nadir"}, 0]},
                {"op": "<", "args": [{"property": "off_nadir"}, 45]},
            ],
        },
        "limit": limit,
    }

    pagination_tester(
        stapi_client=stapi_client,
        endpoint=f"/products/{product_id}/opportunities",
        method="POST",
        limit=limit,
        target="features",
        expected_returns=expected_returns,
        body=request_payload,
    )
