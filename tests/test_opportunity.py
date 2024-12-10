from datetime import UTC, datetime, timedelta
from typing import List

import pytest
from fastapi.testclient import TestClient

from stapi_fastapi.models.opportunity import Opportunity, OpportunityCollection

from .backends import MockProductBackend
from .test_datetime_interval import rfc3339_strftime


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

    # Prepare the request payload
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

    # Construct the endpoint URL using the `product_name` parameter
    url = f"/products/{product_id}/opportunities"

    # Use POST method to send the payload
    response = stapi_client.post(url, json=request_payload)

    # Validate response status and structure
    assert response.status_code == 200, f"Failed for product: {product_id}"
    body = response.json()

    try:
        _ = OpportunityCollection(**body)
    except Exception as _:
        pytest.fail("response is not an opportunity collection")

    assert_link(f"POST {url}", body, "create-order", f"/products/{product_id}/orders")
