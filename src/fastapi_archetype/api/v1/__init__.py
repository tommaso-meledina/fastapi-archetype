from fastapi import APIRouter

from fastapi_archetype.api.v1.dummy_routes import router as dummy_router

__all__ = ["router"]

router = APIRouter(prefix="/v1")
router.include_router(dummy_router)
