from functools import partial
from typing import Any, Optional

from fastapi import Depends, Request, Response
from fastapi.routing import APIRouter
from fastapi_pagination import Page
from typing_extensions import Annotated

import api.models as models
from api.schemas import (
    Session,
    SessionCreate,
    SessionUpdate,
)
from api.services import SessionService, get_session_service
from core.db import foreign_key

router = APIRouter(prefix="/session")


def build_transformer(request: Request, **context):
    "Builds a 'transformer' which allows inject_urls to be run on a list of objects"
    return lambda session: list(map(partial(inject_urls, request=request, **context), session))


def inject_urls(session: models.Session, request: Request, **context):
    """This takes a model along with the request (which, in turn, contains the application context) and
    injects the appropriate urls into the image. A bit of a hacky way to do it, but I couldn't think of another option."""
    if hasattr(session, "backdrop") and session.backdrop is not None:
        session.backdrop.url = request.app.url_path_for(  # type: ignore
            "get_full_image", image_id=session.backdrop.id
        )
        session.backdrop.thumbnail_url = request.app.url_path_for(  # type: ignore
            "get_image_thumbnail", image_id=session.backdrop.id, **context
        )
    if hasattr(session, "overlay_image") and session.overlay_image is not None:
        session.overlay_image.url = request.app.url_path_for(  # type: ignore
            "get_full_image", image_id=session.overlay_image.id
        )
        session.overlay_image.thumbnail_url = request.app.url_path_for(  # type: ignore
            "get_image_thumbnail", image_id=session.overlay_image.id
        )
    session.ws_url = request.app.url_path_for("join_ws", session_id=session.id)  # type: ignore
    return session


@router.get("/", response_model=Page[Session], tags=["sessions"])
async def list_sessions(
    session_service: Annotated[SessionService, Depends(get_session_service)], request: Request
) -> Page[models.Session]:
    "Get all sessions"
    return session_service.get_some(transformer=build_transformer(request))


@router.get(
    "/{session_id}",
    response_model=Session,
    responses={404: {"description": "Session not found"}},
    tags=["sessions"],
)
async def get_session(
    session_id: foreign_key,
    session_service: Annotated[SessionService, Depends(get_session_service)],
    request: Request,
    # current_user: CurrentActiveUser,
) -> Optional[models.Session]:
    "Get a single session by id"
    return inject_urls(session_service.get(session_id), request)


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
    # This needs extensive checking
    # If mode is changed need to check if all acceptable fields are there! Can this be done through pydantic?
    return session_service.update(session_id, session)


@router.delete("/{session_id}", tags=["sessions"])  # , status_code=204)
async def delete_session(
    session_id: foreign_key,
    session_service: Annotated[SessionService, Depends(get_session_service)],
    # current_user: CurrentActiveUser,
) -> Any:
    session_service.delete(session_id)
    return Response(status_code=204)
