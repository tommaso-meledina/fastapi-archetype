from fastapi import APIRouter, Depends, Request, Response, status
from sqlmodel import Session

from fastapi_archetype.auth.dependencies import require_auth
from fastapi_archetype.auth.models import Principal
from fastapi_archetype.core.config import settings
from fastapi_archetype.core.constants import DUMMIES
from fastapi_archetype.core.database import get_session
from fastapi_archetype.core.errors import AppException, ErrorCode
from fastapi_archetype.core.rate_limit import limiter
from fastapi_archetype.factories.dummy import (
    entity_to_get_response,
    entity_to_post_response,
    post_dto_to_entity,
    put_dto_to_entity,
)
from fastapi_archetype.models.dto.v1.dummy import (
    GetDummiesResponse,
    PostDummiesRequest,
    PostDummiesResponse,
    PutDummiesRequest,
)
from fastapi_archetype.services.contracts.dummy_service import (
    DummyServiceV1Contract,
)
from fastapi_archetype.services.v1.dummy_service import get_dummy_service_v1

router = APIRouter(prefix=DUMMIES.path, tags=[DUMMIES.name])


@router.get("", response_model=list[GetDummiesResponse])
@limiter.limit(settings.rate_limit_get_dummies)
def list_dummies(
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
    svc: DummyServiceV1Contract = Depends(get_dummy_service_v1),
) -> list[GetDummiesResponse]:
    entities = svc.get_all_dummies(session)
    return [entity_to_get_response(e) for e in entities]


@router.post(
    "", response_model=PostDummiesResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit(settings.rate_limit_post_dummies)
def create_dummy(
    request: Request,
    dummy: PostDummiesRequest,
    response: Response,
    principal: Principal = Depends(require_auth),
    session: Session = Depends(get_session),
    svc: DummyServiceV1Contract = Depends(get_dummy_service_v1),
) -> PostDummiesResponse:
    _ = principal
    entity = post_dto_to_entity(dummy)
    created = svc.create_dummy(session, entity)
    return entity_to_post_response(created)


@router.put("/{uuid}", response_model=GetDummiesResponse)
def update_dummy(
    uuid: str,
    body: PutDummiesRequest,
    session: Session = Depends(get_session),
    svc: DummyServiceV1Contract = Depends(get_dummy_service_v1),
) -> GetDummiesResponse:
    if body.uuid != uuid:
        raise AppException(
            ErrorCode.BAD_REQUEST,
            detail="Path UUID and body UUID must match",
        )
    entity = put_dto_to_entity(body)
    updated = svc.update_dummy(session, entity)
    return entity_to_get_response(updated)
