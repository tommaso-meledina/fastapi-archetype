from fastapi import APIRouter

from fastapi_archetype.api.v2.dummy_routes import router as dummy_router

router = APIRouter(prefix="/v2")
router.include_router(dummy_router)
