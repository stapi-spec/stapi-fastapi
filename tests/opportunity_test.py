import pytest
from typing import List
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from stapi_fastapi.models.opportunity import Opportunity, OpportunityProperties
from stapi_fastapi.models.product import Product
from stapi_fastapi_test_backend.backend import TestBackend

@pytest.mark.parametrize("product_id", ["umbra-spotlight-1"])
def test_search_opportunities_response(
    product_id: str,
    mock_products: list[Product],
    mock_umbra_spotlight_opportunities: List[Opportunity],
    stapi_backend: TestBackend,
    stapi_client: TestClient,
):
    stapi_backend._products = mock_products
    stapi_backend._opportunities = mock_umbra_spotlight_opportunities

    now = datetime.now(UTC)
    start = now
    end = start + timedelta(days=5)

    # Create mock products and opportunities for the test
    mock_products[0].id = product_id

    # Prepare the request payload
    request_payload = {
        "geometry": {
            "type": "Point",
            "coordinates": [0, 0],
        },
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
    assert isinstance(response.json(), list), "Response should be a list of opportunities"
    for opportunity in response.json():
        assert "id" in opportunity, "Opportunity item should have an 'id' field"
        assert "properties" in opportunity, "Opportunity item should have a 'properties' field"