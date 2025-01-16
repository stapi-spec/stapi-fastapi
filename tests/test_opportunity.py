from datetime import UTC, datetime, timedelta, timezone
from typing import List
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from geojson_pydantic import Point
from geojson_pydantic.types import Position2D

from stapi_fastapi.models.opportunity import Opportunity, OpportunityCollection
from tests.application import MyOpportunityProperties
from tests.conftest import pagination_tester

from .backends import MockProductBackend
from .test_datetime_interval import rfc3339_strftime


@pytest.fixture
def mock_test_spotlight_opportunities() -> list[Opportunity]:
    """Fixture to create mock data for Opportunities for `test-spotlight-1`."""
    now = datetime.now(timezone.utc)  # Use timezone-aware datetime
    start = now
    end = start + timedelta(days=5)

    # Create a list of mock opportunities for the given product
    return [
        Opportunity(
            id=str(uuid4()),
            type="Feature",
            geometry=Point(
                type="Point",
                coordinates=Position2D(longitude=0.0, latitude=0.0),
            ),
            properties=MyOpportunityProperties(
                product_id="xyz123",
                datetime=(start, end),
                off_nadir={"minimum": 20, "maximum": 22},
                vehicle_id=[1],
                platform="platform_id",
            ),
        ),
    ]


@pytest.fixture
def mock_test_pagination_opportunities(
    mock_test_spotlight_opportunities,
) -> list[Opportunity]:
    return [opp for opp in mock_test_spotlight_opportunities for __ in range(0, 3)]


@pytest.mark.parametrize("product_id", ["test-spotlight"])
def test_search_opportunities_response(
    product_id: str,
    mock_test_spotlight_opportunities: List[Opportunity],
    product_backend: MockProductBackend,
    stapi_client: TestClient,
    assert_link,
) -> None:
    product_backend._opportunities = mock_test_spotlight_opportunities

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
    }

    url = f"/products/{product_id}/opportunities"

    response = stapi_client.post(url, json=request_payload)

    assert response.status_code == 200, f"Failed for product: {product_id}"
    body = response.json()

    try:
        _ = OpportunityCollection(**body)
    except Exception as _:
        pytest.fail("response is not an opportunity collection")

    assert_link(f"POST {url}", body, "create-order", f"/products/{product_id}/orders")


@pytest.mark.parametrize("product_id", ["test-spotlight"])
def test_search_opportunities_pagination(
    product_id: str,
    stapi_client: TestClient,
    product_backend: MockProductBackend,
    mock_test_pagination_opportunities: List[Opportunity],
) -> None:
    product_backend._opportunities = mock_test_pagination_opportunities
    expected_returns = [
        x.model_dump(mode="json") for x in mock_test_pagination_opportunities
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
    }

    pagination_tester(
        stapi_client=stapi_client,
        endpoint=f"/products/{product_id}/opportunities",
        method="POST",
        limit=2,
        target="features",
        expected_returns=expected_returns,
        body=request_payload,
    )
