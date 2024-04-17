import json
from datetime import datetime
from typing import cast

import pytz
from fastapi import Request
from pydantic import BaseModel, Field, ValidationError, model_validator
from shapely.geometry import shape

from stat_fastapi.exceptions import ConstraintsException, NotFoundException
from stat_fastapi.models.opportunity import (
    Opportunity,
    OpportunityProperties,
    OpportunitySearch,
)
from stat_fastapi.models.order import Order
from stat_fastapi.models.product import Product, Provider, ProviderRole
from stat_fastapi_landsat.models import (
    ValidatedOpportunitySearch,
)
from stat_fastapi_landsat.repository import Repository
from stat_fastapi_landsat.settings import Settings


class OffNadirRange(BaseModel):
    minimum: float = Field(ge=0.0, le=45)
    maximum: float = Field(ge=0.0, le=45)

    @model_validator(mode="after")
    def validate(self) -> "OffNadirRange":
        diff = self.maximum - self.minimum
        if diff < 5.0:
            raise ValueError("range must be at least 5°")
        return self


class Constraints(BaseModel):
    off_nadir: OffNadirRange = OffNadirRange(minimum=0.0, maximum=30.0)


PRODUCTS = [
    Product(
        id="landsat:8",
        description="Landsat 8",
        license="CC0-1.0",
        providers=[
            Provider(
                name="ACME",
                roles=[
                    ProviderRole.licensor,
                    ProviderRole.producer,
                    ProviderRole.processor,
                    ProviderRole.host,
                ],
                url="http://acme.example.com",
            )
        ],
        constraints=Constraints,
        links=[],
    ),
    Product(
        id="landsat:9",
        description="Landsat 9",
        license="CC0-1.0",
        providers=[
            Provider(
                name="ACME",
                roles=[
                    ProviderRole.licensor,
                    ProviderRole.producer,
                    ProviderRole.processor,
                    ProviderRole.host,
                ],
                url="http://acme.example.com",
            )
        ],
        constraints=Constraints,
        links=[],
    ),
]


class StatLandsatBackend:
    repository: Repository

    def __init__(self):
        settings = Settings.load()
        self.repository = Repository(settings.database)
        self.wrs = {
            "ascending": self._load_json(
                "stat_fastapi_landsat/files/wrs2ascending.geojson"
            ),
            "descending": self._load_json(
                "stat_fastapi_landsat/files/wrs2descending.geojson"
            ),
        }
        self.satellite = self._load_json("stat_fastapi_landsat/files/satellites.json")

    def products(self, request: Request) -> list[Product]:
        """
        Return a list of supported products.
        """
        return PRODUCTS

    def product(self, product_id: str, request: Request) -> Product | None:
        """
        Return the product identified by `product_id` or `None` if it isn't
        supported.
        """
        try:
            return next((product for product in PRODUCTS if product.id == product_id))
        except StopIteration as exc:
            raise NotFoundException() from exc

    async def search_opportunities(
        self, search: OpportunitySearch, request: Request
    ) -> list[Opportunity]:
        """
        Search for ordering opportunities for the given search parameters.
        """
        opportunities = []

        dt_start = cast(tuple, search.datetime)[0]
        dt_end = cast(tuple, search.datetime)[1]

        poi = shape(search.geometry)
        cell_numbers = set(self._find_wrs_cell(poi, self.wrs["ascending"])).union(
            set(self._find_wrs_cell(poi, self.wrs["descending"]))
        )

        if search.product_id == "landsat:8":
            satellite_id = "landsat_8"
        elif search.product_id == "landsat:9":
            satellite_id = "landsat_9"
        else:
            raise NotFoundException()

        if satellite_id in self.satellite:
            for date_str in self.satellite[satellite_id]:
                current_date = datetime.strptime(date_str, "%m/%d/%Y")
                current_date = current_date.astimezone(pytz.utc)

                if dt_start <= current_date <= dt_end:
                    path_list = [
                        int(path)
                        for path in self.satellite[satellite_id][date_str][
                            "path"
                        ].split(",")
                    ]

                    # Check if any path from the satellite data matches the paths from the WRS-2 files
                    for path_of_interest, row, geometry in cell_numbers:
                        if path_of_interest in path_list:
                            opportunities.append(
                                Opportunity(
                                    geometry=geometry,
                                    properties=OpportunityProperties(
                                        product_id=search.product_id,
                                        datetime=[current_date, current_date],
                                        constraints=search.constraints,
                                    ),
                                )
                            )
                            print(
                                f"Satellite: {satellite_id}, Date: {current_date}, Path: {path_of_interest}, Row: {row}, Data: {self.satellite[satellite_id][date_str]}"
                            )

        return opportunities

    async def create_order(self, search: OpportunitySearch, request: Request) -> Order:
        """
        Create a new order.
        """
        try:
            validated = ValidatedOpportunitySearch(**search.model_dump(by_alias=True))
        except ValidationError as exc:
            error_dict = {str(index): error for index, error in enumerate(exc.errors())}
            raise ConstraintsException(error_dict) from exc

        return self.repository.add_order(validated)

    async def get_order(self, order_id: str, request: Request):
        """
        Show details for order with `order_id`.
        """
        feature = self.repository.get_order(order_id)
        if feature is None:
            raise NotFoundException()
        return feature

    def _load_json(self, file_path):
        with open(file_path) as f:
            return json.load(f)

    def _find_wrs_cell(self, poi, geojson_data):
        for feature in geojson_data["features"]:
            if shape(feature["geometry"]).contains(poi):
                path = feature["properties"]["PATH"]
                row = feature["properties"]["ROW"]
                geometry = shape(feature["geometry"])
                yield (path, row, geometry)
