from datetime import UTC, datetime, timedelta

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from geojson_pydantic import Point
from geojson_pydantic.types import Position2D
from httpx import Response

from stapi_fastapi.models.order import OrderPayload

from .application import MyOrderParameters
from .shared import find_link

NOW = datetime.now(UTC)
START = NOW
END = START + timedelta(days=5)


@pytest.fixture
def create_order_payload() -> OrderPayload:
    return OrderPayload(
        geometry=Point(
            type="Point", coordinates=Position2D(longitude=13.4, latitude=52.5)
        ),
        datetime=(
            datetime.fromisoformat("2024-11-11T18:55:33Z"),
            datetime.fromisoformat("2024-11-15T18:55:33Z"),
        ),
        filter=None,
        order_parameters=MyOrderParameters(s3_path="s3://my-bucket"),
    )


@pytest.fixture
def new_order_response(
    product_id: str,
    stapi_client: TestClient,
    create_order_payload: OrderPayload,
) -> Response:
    res = stapi_client.post(
        f"products/{product_id}/orders",
        json=create_order_payload.model_dump(),
    )

    assert res.status_code == status.HTTP_201_CREATED, res.text
    assert res.headers["Content-Type"] == "application/geo+json"
    return res


@pytest.mark.parametrize("product_id", ["test-spotlight"])
def test_new_order_location_header_matches_self_link(
    new_order_response: Response,
) -> None:
    order = new_order_response.json()
    link = find_link(order["links"], "self")
    assert link
    assert new_order_response.headers["Location"] == str(link["href"])


@pytest.mark.parametrize("product_id", ["test-spotlight"])
def test_new_order_links(new_order_response: Response, assert_link) -> None:
    order = new_order_response.json()
    assert_link(
        f"GET /orders/{order['id']}",
        order,
        "monitor",
        f"/orders/{order['id']}/statuses",
    )

    assert_link(
        f"GET /orders/{order['id']}",
        order,
        "self",
        f"/orders/{order['id']}",
        media_type="application/geo+json",
    )


@pytest.fixture
def get_order_response(
    stapi_client: TestClient, new_order_response: Response
) -> Response:
    order_id = new_order_response.json()["id"]

    res = stapi_client.get(f"/orders/{order_id}")
    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/geo+json"
    return res


@pytest.mark.parametrize("product_id", ["test-spotlight"])
def test_get_order_properties(
    get_order_response: Response, create_order_payload
) -> None:
    order = get_order_response.json()

    assert order["geometry"] == {
        "type": "Point",
        "coordinates": list(create_order_payload.geometry.coordinates),
    }

    assert order["properties"]["search_parameters"]["geometry"] == {
        "type": "Point",
        "coordinates": list(create_order_payload.geometry.coordinates),
    }

    assert (
        order["properties"]["search_parameters"]["datetime"]
        == create_order_payload.model_dump()["datetime"]
    )


@pytest.mark.parametrize("product_id", ["test-spotlight"])
def test_order_status_after_create(
    get_order_response: Response, stapi_client: TestClient, assert_link
) -> None:
    body = get_order_response.json()
    assert_link(
        f"GET /orders/{body['id']}", body, "monitor", f"/orders/{body['id']}/statuses"
    )
    link = find_link(body["links"], "monitor")
    assert link is not None

    res = stapi_client.get(link["href"])
    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/json"
    assert len(res.json()["statuses"]) == 1
