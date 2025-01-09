from datetime import UTC, datetime, timedelta

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from geojson_pydantic import Point
from geojson_pydantic.types import Position2D
from httpx import Response

from stapi_fastapi.models.order import OrderPayload

from .application import MyOrderParameters
from .backends import MockProductBackend
from .shared import find_link

NOW = datetime.now(UTC)
START = NOW
END = START + timedelta(days=5)


@pytest.fixture
def create_order_allowed_payloads() -> list[OrderPayload]:
    return [
        OrderPayload(
            geometry=Point(
                type="Point", coordinates=Position2D(longitude=13.4, latitude=52.5)
            ),
            datetime=(
                datetime.fromisoformat("2024-11-11T18:55:33Z"),
                datetime.fromisoformat("2024-11-15T18:55:33Z"),
            ),
            filter=None,
            order_parameters=MyOrderParameters(s3_path="s3://my-bucket"),
        ),
    ]


@pytest.fixture
def new_order_response(
    product_id: str,
    product_backend: MockProductBackend,
    stapi_client: TestClient,
    create_order_allowed_payloads: list[OrderPayload],
) -> Response:
    product_backend._allowed_payloads = create_order_allowed_payloads

    res = stapi_client.post(
        f"products/{product_id}/orders",
        json=create_order_allowed_payloads[0].model_dump(),
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
    get_order_response: Response, create_order_allowed_payloads
) -> None:
    order = get_order_response.json()

    assert order["geometry"] == {
        "type": "Point",
        "coordinates": list(create_order_allowed_payloads[0].geometry.coordinates),
    }

    assert order["properties"]["search_parameters"]["geometry"] == {
        "type": "Point",
        "coordinates": list(create_order_allowed_payloads[0].geometry.coordinates),
    }

    assert (
        order["properties"]["search_parameters"]["datetime"]
        == create_order_allowed_payloads[0].model_dump()["datetime"]
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

    res = stapi_client.get(link["href"])
    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/json"
    assert len(res.json()["statuses"]) == 1


@pytest.mark.parametrize("product_id", ["test-spotlight"])
def test_order_status_after_update(
    get_order_response: Response, stapi_client: TestClient
) -> None:
    body = get_order_response.json()
    statuses_url = find_link(body["links"], "monitor")["href"]

    res = stapi_client.post(
        statuses_url,
        json={
            "status_code": "accepted",
            "reason_code": "REASON1",
            "reason_text": "some reason",
        },
    )

    assert res.status_code == status.HTTP_202_ACCEPTED

    res = stapi_client.get(statuses_url)
    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/json"
    body = res.json()
    assert len(body["statuses"]) == 2

    s = body["statuses"][0]
    assert s["reason_code"] == "REASON1"
    assert s["reason_text"] == "some reason"
    assert s["status_code"] == "accepted"
    assert s["timestamp"]

    s = body["statuses"][1]
    assert s["reason_code"] is None
    assert s["reason_text"] is None
    assert s["status_code"] == "received"
    assert s["timestamp"]


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


def test_empty_order(stapi_client: TestClient):
    res = stapi_client.get("/orders")
    default_orders = {"type": "FeatureCollection", "features": [], "links": []}
    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/geo+json"
    assert res.json() == default_orders


@pytest.fixture
def prepare_order_pagination(
    stapi_client: TestClient, create_order_payloads: list[OrderPayload]
) -> None:
    product_id = "test-spotlight"
    # get uuids created to use as pagination tokens
    for payload in create_order_payloads:
        res = stapi_client.post(
            f"products/{product_id}/orders",
            json=payload.model_dump(),
        )
        assert res.status_code == status.HTTP_201_CREATED, res.text
        assert res.headers["Content-Type"] == "application/geo+json"

    res = stapi_client.get("/orders")
    checker = res.json()
    assert len(checker["features"]) == 3


def test_order_pagination(
    prepare_order_pagination,
    stapi_client: TestClient,
) -> None:
    # prepare_order_pagination

    res = stapi_client.get("/orders", params={"next": None, "limit": 1})
    assert res.status_code == status.HTTP_200_OK
    body = res.json()
    next = body["links"][0]["href"]

    while next:
        res = stapi_client.get(next)
        assert res.status_code == status.HTTP_200_OK
        body = res.json()
        if body["links"]:
            next = body["links"][0]["href"]
        else:
            break


# separate test here to check for bad token getting back 404
def test_token_not_found(stapi_client: TestClient):
    res = stapi_client.get("/orders", params={"next": "a_token"})
    # should return 404 as a result of bad token
    assert res.status_code == status.HTTP_404_NOT_FOUND
