from datetime import UTC, datetime, timedelta

from fastapi import status
from fastapi.testclient import TestClient

from stapi_fastapi.models.opportunity import Opportunity, OpportunityCollection
from stapi_fastapi.models.product import Product
from stapi_fastapi_test_backend.backend import TestBackend


def test_search_opportunities_response(
    products: list[Product],
    opportunities: list[Opportunity],
    stapi_backend: TestBackend,
    stapi_client: TestClient,
):
    stapi_backend._products = products
    stapi_backend._opportunities = opportunities

    now = datetime.now(UTC)
    start = now
    end = start + timedelta(days=5)

    res = stapi_client.post(
        "/opportunities",
        json={
            "geometry": {
                "type": "Point",
                "coordinates": [0, 0],
            },
            "product_id": products[0].id,
            "datetime": f"{start.isoformat()}/{end.isoformat()}",
            "filter": {
                "op": "and",
                "args": [
                    {"op": ">", "args": [{"property": "off_nadir"}, 0]},
                    {"op": "<", "args": [{"property": "off_nadir"}, 45]},
                ],
            },
        },
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/geo+json"
    response = OpportunityCollection(**res.json())

    assert len(response.features) > 0
