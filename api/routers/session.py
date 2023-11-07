from typing import Any, List, Optional

from fastapi import Depends, Response, status
from fastapi.routing import APIRouter
from fastapi_pagination import Page
from typing_extensions import Annotated

import api.models as models
from core.db import foreign_key
from api.schemas import (
    Session,
    SessionCreate,
    SessionUpdate,
)
from api.services import get_session_service
# from api.db.schemas.filters import SessionFilter, generate_filter_query
# from api.deps import CurrentActiveUser
from api.services import SessionService

router = APIRouter(prefix="/session")

@router.get("/", response_model=Page[Session], tags=["sessions"])
async def list_sessions(
    session_service: Annotated[SessionService, Depends(get_session_service)],
    # session_filter: Annotated[SessionFilter, Depends()],
    # current_user: CurrentActiveUser,
) -> Page[models.Session]:
    "Get all sessions"
    return session_service.get_all()


@router.get(
    "/{session_id}",
    response_model=Session,
    responses={404: {"description": "Session not found"}},
    tags=["sessions"],
)
async def get_session(
    session_id: foreign_key,
    session_service: Annotated[SessionService, Depends(get_session_service)],
    # current_user: CurrentActiveUser,
) -> Optional[Session]:
    "Get a single session by id"
    return session_service.get(session_id)


@router.post(
    "/",
    response_model=Session,
    status_code=201,
    responses={409: {"description": "Conflict Error"}},
    tags=["sessions"],
)
async def create_session(
    session: SessionCreate,
    session_service: Annotated[SessionService, Depends(get_session_service)],
    # current_user: CurrentActiveUser,
) -> models.Session:
    "Create a new session"
    return session_service.create(session)


@router.patch("/{session_id}", response_model=Session, tags=["sessions"])
async def update_session(
    session_id: foreign_key,
    session: SessionUpdate,
    session_service: Annotated[SessionService, Depends(get_session_service)],
    # current_user: CurrentActiveUser,
) -> Optional[models.Session]:
    return session_service.update(session_id, session)


@router.delete("/{session_id}", tags=["sessions"])  # , status_code=204)
async def delete_session(
    session_id: foreign_key,
    session_service: Annotated[SessionService, Depends(get_session_service)],
    # current_user: CurrentActiveUser,
) -> Any:
    session_service.delete(session_id)
    return Response(status_code=204)