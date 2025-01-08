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


@pytest.fixture
def prepare_order_pagination(
    stapi_client: TestClient, create_order_payloads: list[OrderPayload]
) -> tuple[str, str, str]:
    # product_backend._allowed_payloads = create_order_payloads
    product_id = "test-spotlight"

    # # check empty
    # res = stapi_client.get("/orders")
    # default_orders = {"type": "FeatureCollection", "features": [], "links": []}
    # assert res.status_code == status.HTTP_200_OK
    # assert res.headers["Content-Type"] == "application/geo+json"
    # assert res.json() == default_orders

    # get uuids created to use as pagination tokens
    order_ids = []
    for payload in create_order_payloads:
        res = stapi_client.post(
            f"products/{product_id}/orders",
            json=payload.model_dump(),
        )
        assert res.status_code == status.HTTP_201_CREATED, res.text
        assert res.headers["Content-Type"] == "application/geo+json"
        order_ids.append(res.json()["id"])

    # res = stapi_client.get("/orders")
    # checker = res.json()
    # assert len(checker['features']) == 3

    return tuple(order_ids)


@pytest.mark.parametrize(
    "product_id,expected_status,limit,id_retrieval,token_back",
    [
        pytest.param(
            "test-spotlight",
            status.HTTP_200_OK,
            1,
            0,
            True,
            id="input frst order_id token get new token back",
        ),
        pytest.param(
            "test-spotlight",
            status.HTTP_200_OK,
            1,
            2,
            False,
            id="input last order_id token get NO token back",
        ),
        pytest.param(
            "test-spotlight",
            status.HTTP_404_NOT_FOUND,
            1,
            "BAD_TOKEN",
            False,
            id="input bad token get 404 back",
        ),
        pytest.param(
            "test-spotlight",
            status.HTTP_200_OK,
            1,
            1000000,
            False,
            id="high limit handled and returns valid records",
        ),
    ],
)
def test_order_pagination(
    prepare_order_pagination,
    stapi_client: TestClient,
    product_id: str,
    expected_status: int,
    limit: int,
    id_retrieval: int | str,
    token_back: bool,
) -> None:
    order_ids = prepare_order_pagination

    res = stapi_client.get(
        "/orders", params={"next": order_ids[id_retrieval], "limit": limit}
    )
    assert res.status_code == expected_status

    body = res.json()
    for link in body["features"][0]["links"]:
        assert link["rel"] != "next"
    assert body["links"] != []

    # check to make sure new token in link
    if token_back:
        assert order_ids[id_retrieval] not in body["links"][0]["href"]

        assert len(body["features"]) == limit


# test cases to check
# 1. Input token and get last record.  Should not return a token if we are returning the last record - 'last' record being what is sorted
# 2. Input a crzy high limit - how to handle?  Default to max or all records if less than max
# 3. Input token and get some intermediate records - return a token for next records
# 4. handle requesting an orderid/token that does't exist and returns 400/404. Bad token --> bad request.
