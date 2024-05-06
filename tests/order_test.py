from datetime import UTC, datetime, timedelta
from typing import Generator

from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response
from pytest import fixture

from stapi_fastapi.models.opportunity import OpportunityRequest
from stapi_fastapi_test_backend.backend import TestBackend

from .utils import find_link

NOW = datetime.now(UTC)
START = NOW
END = START + timedelta(days=5)


@fixture
def new_order_response(
    stapi_backend: TestBackend,
    stapi_client: TestClient,
    allowed_payloads: list[OpportunityRequest],
) -> Generator[Response, None, None]:
    stapi_backend._allowed_payloads = allowed_payloads

    res = stapi_client.post(
        "/orders",
        json=allowed_payloads[0].model_dump(),
    )

    assert res.status_code == status.HTTP_201_CREATED
    assert res.headers["Content-Type"] == "application/geo+json"
    yield res


def test_new_order_location_header_matches_self_link(new_order_response: Response):
    order = new_order_response.json()
    assert new_order_response.headers["Location"] == str(
        find_link(order["links"], "self")["href"]
    )


@fixture
def get_order_response(
    stapi_client: TestClient, new_order_response: Response
) -> Generator[Response, None, None]:
    order_id = new_order_response.json()["id"]

    res = stapi_client.get(f"/orders/{order_id}")
    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/geo+json"
    yield res


def test_get_order_properties(get_order_response: Response, allowed_payloads):
    order = get_order_response.json()

    assert order["geometry"] == {
        "type": "Point",
        "coordinates": list(allowed_payloads[0].geometry.coordinates),
    }

    assert (
        order["properties"]["datetime"] == allowed_payloads[0].model_dump()["datetime"]
    )
