from datetime import UTC, datetime, timedelta, timezone
from typing import Any, Callable
from uuid import uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from stapi_fastapi.models.opportunity import (
    OpportunityCollection,
    OpportunitySearchRecord,
    OpportunitySearchStatus,
    OpportunitySearchStatusCode,
)
from stapi_fastapi.models.shared import Link

from .shared import (
    create_mock_opportunity,
    find_link,
    pagination_tester,
    product_test_spotlight,
    product_test_spotlight_async_opportunity,
    product_test_spotlight_sync_async_opportunity,
    product_test_spotlight_sync_opportunity,
)
from .test_datetime_interval import rfc3339_strftime


@pytest.mark.mock_products([product_test_spotlight])
def test_no_opportunity_search_advertised(stapi_client: TestClient) -> None:
    product_id = "test-spotlight"

    # the `/products/{productId}/opportunities link should not be advertised on the product
    product_response = stapi_client.get(f"/products/{product_id}")
    product_body = product_response.json()
    assert find_link(product_body["links"], "opportunities") is None

    # the `searches/opportunities` link should not be advertised on the root
    root_response = stapi_client.get("/")
    root_body = root_response.json()
    assert find_link(root_body["links"], "opportunity-search-records") is None


@pytest.mark.mock_products([product_test_spotlight_sync_opportunity])
def test_only_sync_search_advertised(stapi_client: TestClient) -> None:
    product_id = "test-spotlight"

    # the `/products/{productId}/opportunities link should be advertised on the product
    product_response = stapi_client.get(f"/products/{product_id}")
    product_body = product_response.json()
    assert find_link(product_body["links"], "opportunities")

    # the `searches/opportunities` link should not be advertised on the root
    root_response = stapi_client.get("/")
    root_body = root_response.json()
    assert find_link(root_body["links"], "opportunity-search-records") is None


# test async search offered
@pytest.mark.parametrize(
    "mock_products",
    [
        [product_test_spotlight_async_opportunity],
        [product_test_spotlight_sync_async_opportunity],
    ],
)
def test_async_search_advertised(stapi_client_async_opportunity: TestClient) -> None:
    product_id = "test-spotlight"

    # the `/products/{productId}/opportunities link should be advertised on the product
    product_response = stapi_client_async_opportunity.get(f"/products/{product_id}")
    product_body = product_response.json()
    assert find_link(product_body["links"], "opportunities")

    # the `searches/opportunities` link should be advertised on the root
    root_response = stapi_client_async_opportunity.get("/")
    root_body = root_response.json()
    assert find_link(root_body["links"], "opportunity-search-records")


@pytest.mark.mock_products([product_test_spotlight_async_opportunity])
def test_async_search_response(
    stapi_client_async_opportunity: TestClient,
    opportunity_search: dict[str, Any],
) -> None:
    product_id = "test-spotlight"
    url = f"/products/{product_id}/opportunities"

    response = stapi_client_async_opportunity.post(url, json=opportunity_search)
    assert response.status_code == 201

    body = response.json()
    try:
        _ = OpportunitySearchRecord(**body)
    except Exception as _:
        pytest.fail("response is not an opportunity search record")

    assert find_link(body["links"], "self")


@pytest.mark.mock_products([product_test_spotlight_async_opportunity])
def test_async_search_is_default(
    stapi_client_async_opportunity: TestClient,
    opportunity_search: dict[str, Any],
) -> None:
    product_id = "test-spotlight"
    url = f"/products/{product_id}/opportunities"

    response = stapi_client_async_opportunity.post(url, json=opportunity_search)
    assert response.status_code == 201

    body = response.json()
    try:
        _ = OpportunitySearchRecord(**body)
    except Exception as _:
        pytest.fail("response is not an opportunity search record")


@pytest.mark.mock_products([product_test_spotlight_sync_async_opportunity])
def test_prefer_header(
    stapi_client_async_opportunity: TestClient,
    opportunity_search: dict[str, Any],
) -> None:
    product_id = "test-spotlight"
    url = f"/products/{product_id}/opportunities"

    # prefer = "wait"
    response = stapi_client_async_opportunity.post(
        url, json=opportunity_search, headers={"Prefer": "wait"}
    )
    assert response.status_code == 200
    assert response.headers["Preference-Applied"] == "wait"

    body = response.json()
    try:
        OpportunityCollection(**body)
    except Exception as _:
        pytest.fail("response is not an opportunity collection")

    # prefer = "respond-async"
    response = stapi_client_async_opportunity.post(
        url, json=opportunity_search, headers={"Prefer": "respond-async"}
    )
    assert response.status_code == 201
    assert response.headers["Preference-Applied"] == "respond-async"

    body = response.json()
    try:
        OpportunitySearchRecord(**body)
    except Exception as _:
        pytest.fail("response is not an opportunity search record")


@pytest.mark.mock_products([product_test_spotlight_async_opportunity])
def test_async_search_record_retrieval(
    stapi_client_async_opportunity: TestClient,
    opportunity_search: dict[str, Any],
) -> None:
    # post an async search
    product_id = "test-spotlight"
    url = f"/products/{product_id}/opportunities"
    search_response = stapi_client_async_opportunity.post(url, json=opportunity_search)
    assert search_response.status_code == 201
    search_response_body = search_response.json()

    # get the search record by id and verify it matches the original response
    search_record_id = search_response_body["id"]
    record_response = stapi_client_async_opportunity.get(
        f"/searches/opportunities/{search_record_id}"
    )
    assert record_response.status_code == 200
    record_response_body = record_response.json()
    assert record_response_body == search_response_body

    # verify the search record is in the list of all search records
    records_response = stapi_client_async_opportunity.get("/searches/opportunities")
    assert records_response.status_code == 200
    records_response_body = records_response.json()
    assert search_record_id in [
        x["id"] for x in records_response_body["search_records"]
    ]


@pytest.mark.mock_products([product_test_spotlight_async_opportunity])
def test_async_opportunity_search_to_completion(
    stapi_client_async_opportunity: TestClient,
    opportunity_search: dict[str, Any],
    url_for: Callable[[str], str],
) -> None:
    # Post a request for an async search
    product_id = "test-spotlight"
    url = f"/products/{product_id}/opportunities"
    search_response = stapi_client_async_opportunity.post(url, json=opportunity_search)
    assert search_response.status_code == 201
    search_record = OpportunitySearchRecord(**search_response.json())

    # Simulate the search being completed by some external process:
    # - an OpportunityCollection is created and stored in the database
    collection = OpportunityCollection(
        id=str(uuid4()),
        features=[create_mock_opportunity()],
    )
    collection.links.append(
        Link(
            rel="create-order",
            href=url_for(f"/products/{product_id}/orders"),
            body=search_record.opportunity_request.model_dump(),
            method="POST",
        )
    )
    collection.links.append(
        Link(
            rel="search-record",
            href=url_for(f"/searches/opportunities/{search_record.id}"),
        )
    )

    stapi_client_async_opportunity.app_state[
        "_opportunities_db"
    ].put_opportunity_collection(collection)

    # - the OpportunitySearchRecord links and status are updated in the database
    search_record.links.append(
        Link(
            rel="opportunities",
            href=url_for(f"/products/{product_id}/opportunities/{collection.id}"),
        )
    )
    search_record.status = OpportunitySearchStatus(
        timestamp=datetime.now(timezone.utc),
        status_code=OpportunitySearchStatusCode.completed,
    )

    stapi_client_async_opportunity.app_state["_opportunities_db"].put_search_record(
        search_record
    )

    # Verify we can retrieve the OpportunitySearchRecord by its id and its status is
    # `completed`
    url = f"/searches/opportunities/{search_record.id}"
    retrieved_search_response = stapi_client_async_opportunity.get(url)
    assert retrieved_search_response.status_code == 200
    retrieved_search_record = OpportunitySearchRecord(
        **retrieved_search_response.json()
    )
    assert (
        retrieved_search_record.status.status_code
        == OpportunitySearchStatusCode.completed
    )

    # Verify we can retrieve the OpportunityCollection from the
    # OpportunitySearchRecord's `opportunities` link; verify the retrieved
    # OpportunityCollection contains an order link and a link pointing back to the
    # OpportunitySearchRecord
    opportunities_link = next(
        x for x in retrieved_search_record.links if x.rel == "opportunities"
    )
    url = str(opportunities_link.href)
    retrieved_collection_response = stapi_client_async_opportunity.get(url)
    assert retrieved_collection_response.status_code == 200
    retrieved_collection = OpportunityCollection(**retrieved_collection_response.json())
    assert any(x for x in retrieved_collection.links if x.rel == "create-order")
    assert any(x for x in retrieved_collection.links if x.rel == "search-record")


@pytest.mark.mock_products([product_test_spotlight_async_opportunity])
def test_new_search_location_header_matches_self_link(
    stapi_client_async_opportunity: TestClient,
    opportunity_search: dict[str, Any],
) -> None:
    product_id = "test-spotlight"
    url = f"/products/{product_id}/opportunities"
    search_response = stapi_client_async_opportunity.post(url, json=opportunity_search)
    assert search_response.status_code == 201

    search_record = search_response.json()
    link = find_link(search_record["links"], "self")
    assert link
    assert search_response.headers["Location"] == str(link["href"])


@pytest.mark.mock_products([product_test_spotlight_async_opportunity])
def test_bad_ids(stapi_client_async_opportunity: TestClient) -> None:
    search_record_id = "bad_id"
    res = stapi_client_async_opportunity.get(
        f"/searches/opportunities/{search_record_id}"
    )
    assert res.status_code == status.HTTP_404_NOT_FOUND

    product_id = "test-spotlight"
    opportunity_collection_id = "bad_id"
    res = stapi_client_async_opportunity.get(
        f"/products/{product_id}/opportunities/{opportunity_collection_id}"
    )
    assert res.status_code == status.HTTP_404_NOT_FOUND


@pytest.fixture
def setup_search_record_pagination(
    stapi_client_async_opportunity: TestClient,
) -> list[dict[str, Any]]:
    product_id = "test-spotlight"
    search_records = []
    for _ in range(3):
        now = datetime.now(UTC)
        end = now + timedelta(days=5)
        format = "%Y-%m-%dT%H:%M:%S.%f%z"
        start_string = rfc3339_strftime(now, format)
        end_string = rfc3339_strftime(end, format)

        opportunity_request = {
            "geometry": {
                "type": "Point",
                "coordinates": [0, 0],
            },
            "datetime": f"{start_string}/{end_string}",
            "filter": {
                "op": "and",
                "args": [
                    {"op": ">", "args": [{"property": "off_nadir"}, 0]},
                    {"op": "<", "args": [{"property": "off_nadir"}, 45]},
                ],
            },
        }

        response = stapi_client_async_opportunity.post(
            f"/products/{product_id}/opportunities", json=opportunity_request
        )
        assert response.status_code == 201

        body = response.json()
        search_records.append(body)

    return search_records


@pytest.mark.parametrize("limit", [0, 1, 2, 4])
@pytest.mark.mock_products([product_test_spotlight_async_opportunity])
def test_get_search_records_pagination(
    stapi_client_async_opportunity: TestClient,
    setup_search_record_pagination: list[dict[str, Any]],
    limit: int,
) -> None:
    expected_returns = []
    if limit > 0:
        expected_returns = setup_search_record_pagination

    pagination_tester(
        stapi_client=stapi_client_async_opportunity,
        url="/searches/opportunities",
        method="GET",
        limit=limit,
        target="search_records",
        expected_returns=expected_returns,
    )
