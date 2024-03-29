from datetime import UTC, datetime, timedelta

from fastapi import status
from fastapi.testclient import TestClient
from pytest import fixture

from stat_fastapi.models.opportunity import OpportunityCollection


@fixture
def search_opportunities_response(stat_client: TestClient, product_id: str):
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
            "product_id": product_id,
            "properties": {
                "datetime": f"{start.isoformat()}/{end.isoformat()}",
                "off_nadir": {
                    "minimum": 0,
                    "maximum": 45,
                },
            },
        },
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/geo+json"
    yield OpportunityCollection(**res.json())


def test_search_opportunities_response(
    search_opportunities_response: OpportunityCollection, product_id: str, url_for
):
    response = search_opportunities_response
    assert len(response.features) > 0
