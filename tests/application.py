import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stapi_fastapi.models.conformance import CORE
from stapi_fastapi.routers.root_router import RootRouter
from tests.backends import (
    mock_get_order,
    mock_get_order_statuses,
    mock_get_orders,
)
from tests.shared import InMemoryOrderDB, mock_product_test_spotlight


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[dict[str, Any]]:
    try:
        yield {
            "_orders_db": InMemoryOrderDB(),
        }
    finally:
        pass


root_router = RootRouter(
    get_orders=mock_get_orders,
    get_order=mock_get_order,
    get_order_statuses=mock_get_order_statuses,
    conformances=[CORE],
)
root_router.add_product(mock_product_test_spotlight)
app: FastAPI = FastAPI(lifespan=lifespan)
app.include_router(root_router, prefix="")
