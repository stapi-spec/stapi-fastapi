from fastapi import status
from fastapi.testclient import TestClient

from stapi_fastapi.models.conformance import CORE


def test_conformance(stapi_client: TestClient) -> None:
    res = stapi_client.get("/conformance")

    assert res.status_code == status.HTTP_200_OK
    assert res.headers["Content-Type"] == "application/json"

    body = res.json()

    assert body["conformsTo"] == [CORE]
