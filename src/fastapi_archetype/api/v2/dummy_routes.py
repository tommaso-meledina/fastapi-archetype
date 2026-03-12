from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_archetype.auth.dependencies import require_role
from fastapi_archetype.auth.models import Principal, Role
from fastapi_archetype.core.config import settings
from fastapi_archetype.core.constants import DUMMIES
from fastapi_archetype.core.database import get_session
from fastapi_archetype.core.rate_limit import limiter
from fastapi_archetype.factories.dummy import (
    entity_to_get_response,
    entity_to_post_response,
    post_dto_to_entity,
)
from fastapi_archetype.models.dto.v1.dummy import (
    GetDummiesResponse,
    PostDummiesRequest,
    PostDummiesResponse,
)
from fastapi_archetype.services.factory import DummyServiceV2
from fastapi_archetype.services.v2.dummy_service import get_dummy_service_v2

router = APIRouter(prefix=DUMMIES.path, tags=[f"{DUMMIES.name} v2"])
_depends_require_admin = Depends(require_role(Role.ADMIN))


@router.get("", response_model=list[GetDummiesResponse])
@limiter.limit(settings.rate_limit_get_dummies)
async def list_dummies(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
    svc: DummyServiceV2 = Depends(get_dummy_service_v2),
) -> list[GetDummiesResponse]:
    entities = await svc.get_all_dummies(session)
    return [entity_to_get_response(e) for e in entities]


@router.post(
    "", response_model=PostDummiesResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit(settings.rate_limit_post_dummies)
async def create_dummy(
    request: Request,
    dummy: PostDummiesRequest,
    response: Response,
    principal: Principal = _depends_require_admin,
    session: AsyncSession = Depends(get_session),
    svc: DummyServiceV2 = Depends(get_dummy_service_v2),
) -> PostDummiesResponse:
    _ = principal
    entity = post_dto_to_entity(dummy)
    created = await svc.create_dummy(session, entity)
    return entity_to_post_response(created)
