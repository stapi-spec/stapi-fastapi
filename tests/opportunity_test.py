import json
from datetime import UTC, datetime, timedelta
from typing import List

import pytest
from fastapi.testclient import TestClient
from stapi_fastapi.models.opportunity import Opportunity

from .backend import TestProductBackend
from .datetime_interval_test import rfc3339_strftime


@pytest.mark.parametrize("product_id", ["test-spotlight"])
def test_search_opportunities_response(
    product_id: str,
    mock_test_spotlight_opportunities: List[Opportunity],
    product_backend: TestProductBackend,
    stapi_client: TestClient,
):
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

    print(json.dumps(response.json(), indent=4))

    # Validate response status and structure
    assert response.status_code == 200, f"Failed for product: {product_id}"
    assert isinstance(
        response.json(), list
    ), "Response should be a list of opportunities"
    for opportunity in response.json():
        assert "id" in opportunity, "Opportunity item should have an 'id' field"
        assert (
            "properties" in opportunity
        ), "Opportunity item should have a 'properties' field"
