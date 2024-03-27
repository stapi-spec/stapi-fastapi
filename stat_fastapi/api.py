from fastapi import APIRouter, Request

from stat_fastapi.models.root import RootResponse
from stat_fastapi.models.shared import Link


class StatApiRouter:
    NAME_PREFIX = "stat"
    openapi_endpoint_name: str
    docs_endpoint_name: str
    router: APIRouter

    def __init__(
        self,
        openapi_endpoint_name="openapi",
        docs_endpoint_name="swagger_ui_html",
        *args,
        **kwargs,
    ):
        self.openapi_endpoint_name = openapi_endpoint_name
        self.docs_endpoint_name = docs_endpoint_name

        self.router = APIRouter(*args, **kwargs)
        self.router.add_api_route(
            "/",
            self.root,
            methods=["GET"],
            name=f"{self.NAME_PREFIX}:root",
            tags=["Root"],
        )

    def root(self, request: Request) -> RootResponse:
        return RootResponse(
            links=[
                Link(
                    href=str(request.url_for("stat:root")),
                    rel="self",
                    type="application/json",
                ),
                Link(
                    href=str(request.url_for(self.openapi_endpoint_name)),
                    rel="service-description",
                    type="application/json",
                ),
                Link(
                    href=str(request.url_for(self.docs_endpoint_name)),
                    rel="service-docs",
                    type="text/html",
                ),
            ]
        )
