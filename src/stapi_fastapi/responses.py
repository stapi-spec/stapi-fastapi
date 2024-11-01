from fastapi.responses import JSONResponse

from stapi_fastapi.constants import TYPE_GEOJSON


class GeoJSONResponse(JSONResponse):
    def __init__(self, *args, **kwargs) -> None:
        kwargs["media_type"] = TYPE_GEOJSON
        super().__init__(*args, **kwargs)
