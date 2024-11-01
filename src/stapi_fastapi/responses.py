from fastapi.responses import JSONResponse

from stapi_fastapi.constants import TYPE_GEOJSON


class GeoJSONResponse(JSONResponse):
    media_type = TYPE_GEOJSON
