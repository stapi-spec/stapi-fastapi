from datetime import UTC, datetime, timedelta

from fastapi import status
from fastapi.testclient import TestClient

from stat_fastapi.models.opportunity import Opportunity, OpportunityCollection
from stat_fastapi.models.product import Product
from stat_fastapi_test_backend.backend import TestBackend


def test_search_opportunities_response(
    products: list[Product],
    opportunities: list[Opportunity],
    stat_backend: TestBackend,
    stat_client: TestClient,
):
    stat_backend._products = products
    stat_backend._opportunities = opportunities

    now = datetime.now(UTC)
    start = now
    end = start + timedelta(days=5)

    res = stat_client.post(
        "/opportunities",
        json={
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [0, 0],
            },
            "product_id": products[0].id,
            "datetime": f"{start.isoformat()}/{end.isoformat()}",
            "constraints": {
                "off_nadir": {
                    "minimum": 0,
                    "maximum": 45,
                },
            },
        },
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/geo+json"
    response = OpportunityCollection(**res.json())

    assert len(response.features) > 0
