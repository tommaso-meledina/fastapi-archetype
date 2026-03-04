from __future__ import annotations

from fastapi import APIRouter

from fastapi_archetype.api.dummy_routes import router as dummy_router

router = APIRouter(prefix="/v1")
router.include_router(dummy_router)
