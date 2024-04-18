"""
Umbra Space Product Offerings
"""

from enum import Enum

from pydantic import BaseModel

from stat_fastapi.models.product import Product, Provider, ProviderRole
from stat_fastapi.models.shared import Link


class SceneSizeConstraints(Enum):
    """Scene Size Contraints"""

    SCENE_5X5_KM = "5x5_KM"
    SCENE_10X10_KM = "10x10_KM"


class SpotlightConstraints(BaseModel):
    """Spotlight Constraints"""

    scene_size: SceneSizeConstraints


SPOTLIGHT_PRODUCT = Product(
    id="UMBRA:SPOTLIGHT_TASK",
    title="Umbra spotlight SAR capture",
    description="Umbra Spotlight Product",
    keywords=["sar", "radar", "umbra"],
    license="CC0-1.0",
    providers=[
        Provider(
            name="UMBRA",
            roles=[
                ProviderRole.licensor,
                ProviderRole.producer,
                ProviderRole.processor,
                ProviderRole.host,
            ],
            url="http://umbra.space",
        )
    ],
    links=[],
    constraints=SpotlightConstraints,
)

ARCHIVE_PRODUCT = Product(
    id="UMBRA:SPOTLIGHT_ARCHIVE_TASK",
    title="Umbra SAR spotlight capture from Archive",
    description="Archive task from Umbra's STAC",
    keywords=["sar", "radar", "umbra", "catalog", "archive"],
    license="CC0-1.0",
    providers=[
        Provider(
            name="UMBRA",
            roles=[
                ProviderRole.licensor,
                ProviderRole.producer,
                ProviderRole.processor,
                ProviderRole.host,
            ],
            url="http://umbra.space",
        )
    ],
    links=[Link(href="https://api.canopy.umbra.space/archive/search", rel="catalog")],
    constraints=SpotlightConstraints,
)
PRODUCTS = [SPOTLIGHT_PRODUCT, ARCHIVE_PRODUCT]
