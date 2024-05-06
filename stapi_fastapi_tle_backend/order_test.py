"""
from datetime import UTC, datetime, timedelta
from typing import Generator

from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response
from pytest import fixture

from tests.utils import find_link

NOW = datetime.now(UTC)
START = NOW
END = START + timedelta(days=5)
START_END_INTERVAL = f"{START.isoformat()}/{END.isoformat()}".replace("+00:00", "Z")


@fixture
def new_order_response(
    stapi_client: TestClient, product_id: str
) -> Generator[Response, None, None]:
    res = stapi_client.post(
        "/orders",
        json={
            "type": "Feature",
            "product_id": product_id,
            "geometry": {"type": "Point", "coordinates": [0, 0]},
            "properties": {"datetime": f"{START.isoformat()}/{END.isoformat()}"},
        },
    )

    assert res.status_code == status.HTTP_201_CREATED
    assert res.headers["Content-Type"] == "application/geo+json"
    yield res


def test_new_order_location_header_matches_self_link(new_order_response: Response):
    order = new_order_response.json()
    assert (
        new_order_response.headers["Location"]
        == find_link(order["links"], "self")["href"]
    )


def test_new_order_status_is_pending(new_order_response: Response):
    order = new_order_response.json()
    assert order["properties"]["status"] == "pending"
    assert order["properties"]["off_nadir"] == {"minimum": 0, "maximum": 30}


@fixture
def get_order_response(
    stapi_client: TestClient, new_order_response: Response
) -> Generator[Response, None, None]:
    order_id = new_order_response.json()["id"]

    res = stapi_client.get(f"/orders/{order_id}")

    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/geo+json"
    yield res


def test_get_order_properties(get_order_response: Response):
    order = get_order_response.json()

    assert order["geometry"] == {
        "type": "Point",
        "coordinates": [0, 0],
    }

    assert order["properties"]["datetime"] == START_END_INTERVAL
    assert order["properties"]["status"] == "pending"
    assert order["properties"]["off_nadir"] == {"minimum": 0, "maximum": 30}
"""
