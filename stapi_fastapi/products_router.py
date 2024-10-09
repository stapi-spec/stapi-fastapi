# Generic product router factory
from fastapi import APIRouter, HTTPException, status, Request
from typing import Dict, Any
from stapi_fastapi.models.opportunity import OpportunityRequest
from stapi_fastapi.backend import StapiBackend
from stapi_fastapi.exceptions import ConstraintsException

"""
/products[MainRouter]/opportunities
/products[MainRouter]/parameters
/products[MainRouter]/order
"""

def create_products_router(product_id: str, backend: StapiBackend) -> APIRouter:
    # TODO: map product names to product IDs
    """
    Creates a new APIRouter for a specific product type with standardized routes.

    Args:
        product_id (str): The name of the product type (e.g., 'electronics', 'furniture').
        backend (StapiBackend): Backend instance implementing the StapiBackend protocol.

    Returns:
        APIRouter: A FastAPI APIRouter configured for the product type.
    """
    # Create a new router for the given product type
    router = APIRouter(prefix=f"/{product_id}", tags=[product_id.capitalize()])

    @router.get("/opportunities", summary="Get Opportunities for the product")
    async def get_opportunities(request: Request, search: OpportunityRequest):
        try:
            opportunities = await backend.search_opportunities(search, request)
            return opportunities
        except ConstraintsException as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.detail)

    @router.get("/parameters", summary="Get parameters for the product")
    async def get_product_parameters(request: Request):
        product = backend.product(product_id, request)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"product_id": product.id, "parameters": product.parameters}

    @router.post("/order", summary="Create an order for the product")
    async def create_order(request: Request, payload: OpportunityRequest):
        try:
            order = await backend.create_order(payload, request)
            return order
        except ConstraintsException as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.detail)

    return router