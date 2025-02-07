from datetime import UTC, datetime, timedelta, timezone

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from geojson_pydantic import Point
from geojson_pydantic.types import Position2D
from httpx import Response

from stapi_fastapi.models.order import Order, OrderPayload, OrderStatus, OrderStatusCode

from .shared import MyOrderParameters, find_link, pagination_tester

NOW = datetime.now(UTC)
START = NOW
END = START + timedelta(days=5)


def test_empty_order(stapi_client: TestClient):
    res = stapi_client.get("/orders")
    default_orders = {"type": "FeatureCollection", "features": [], "links": []}
    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/geo+json"
    assert res.json() == default_orders


@pytest.fixture
def create_order_payloads() -> list[OrderPayload]:
    datetimes = [
        ("2024-10-09T18:55:33Z", "2024-10-12T18:55:33Z"),
        ("2024-10-15T18:55:33Z", "2024-10-18T18:55:33Z"),
        ("2024-10-20T18:55:33Z", "2024-10-23T18:55:33Z"),
    ]
    payloads = []
    for start, end in datetimes:
        payload = OrderPayload(
            geometry=Point(
                type="Point", coordinates=Position2D(longitude=14.4, latitude=56.5)
            ),
            datetime=(
                datetime.fromisoformat(start),
                datetime.fromisoformat(end),
            ),
            filter=None,
            order_parameters=MyOrderParameters(s3_path="s3://my-bucket"),
        )
        payloads.append(payload)
    return payloads


@pytest.fixture
def new_order_response(
    product_id: str,
    stapi_client: TestClient,
    create_order_payloads: list[OrderPayload],
) -> Response:
    res = stapi_client.post(
        f"products/{product_id}/orders",
        json=create_order_payloads[0].model_dump(),
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
    get_order_response: Response, create_order_payloads
) -> None:
    order = get_order_response.json()

    assert order["geometry"] == {
        "type": "Point",
        "coordinates": list(create_order_payloads[0].geometry.coordinates),
    }

    assert order["properties"]["search_parameters"]["geometry"] == {
        "type": "Point",
        "coordinates": list(create_order_payloads[0].geometry.coordinates),
    }

    assert (
        order["properties"]["search_parameters"]["datetime"]
        == create_order_payloads[0].model_dump()["datetime"]
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


@pytest.fixture
def setup_orders_pagination(
    stapi_client: TestClient, create_order_payloads
) -> list[Order]:
    product_id = "test-spotlight"
    orders = []
    for order in create_order_payloads:
        res = stapi_client.post(
            f"products/{product_id}/orders",
            json=order.model_dump(),
        )
        body = res.json()
        orders.append(body)

        assert res.status_code == status.HTTP_201_CREATED, res.text
        assert res.headers["Content-Type"] == "application/geo+json"

    return orders


@pytest.mark.parametrize("limit", [0, 1, 2, 4])
def test_get_orders_pagination(
    limit, setup_orders_pagination, create_order_payloads, stapi_client: TestClient
) -> None:
    expected_returns = []
    if limit > 0:
        expected_returns = setup_orders_pagination

    pagination_tester(
        stapi_client=stapi_client,
        url="/orders",
        method="GET",
        limit=limit,
        target="features",
        expected_returns=expected_returns,
    )


def test_token_not_found(stapi_client: TestClient) -> None:
    res = stapi_client.get("/orders", params={"next": "a_token"})
    assert res.status_code == status.HTTP_404_NOT_FOUND


@pytest.fixture
def order_statuses() -> dict[str, list[OrderStatus]]:
    statuses = {
        "test_order_id": [
            OrderStatus(
                timestamp=datetime(2025, 1, 14, 2, 21, 48, 466726, tzinfo=timezone.utc),
                status_code=OrderStatusCode.received,
                links=[],
            ),
            OrderStatus(
                timestamp=datetime(2025, 1, 15, 5, 20, 48, 466726, tzinfo=timezone.utc),
                status_code=OrderStatusCode.accepted,
                links=[],
            ),
            OrderStatus(
                timestamp=datetime(
                    2025, 1, 16, 10, 15, 32, 466726, tzinfo=timezone.utc
                ),
                status_code=OrderStatusCode.completed,
                links=[],
            ),
        ]
    }
    return statuses


@pytest.mark.parametrize("limit", [0, 1, 2, 4])
def test_get_order_status_pagination(
    limit: int,
    stapi_client: TestClient,
    order_statuses: dict[str, list[OrderStatus]],
) -> None:
    for id, statuses in order_statuses.items():
        for s in statuses:
            stapi_client.app_state["_orders_db"].put_order_status(id, s)

    order_id = "test_order_id"
    expected_returns = []
    if limit != 0:
        expected_returns = [x.model_dump(mode="json") for x in order_statuses[order_id]]

    pagination_tester(
        stapi_client=stapi_client,
        url=f"/orders/{order_id}/statuses",
        method="GET",
        limit=limit,
        target="statuses",
        expected_returns=expected_returns,
    )


def test_get_order_statuses_bad_token(
    stapi_client: TestClient,
    order_statuses: dict[str, list[OrderStatus]],
    limit: int = 2,
) -> None:
    stapi_client.app_state["_orders_db"]._statuses = order_statuses

    order_id = "non_existing_order_id"
    res = stapi_client.get(f"/orders/{order_id}/statuses")
    assert res.status_code == status.HTTP_404_NOT_FOUND
