from typing import Any, List, Optional

from fastapi import Depends, Response, status
from fastapi.routing import APIRouter
from fastapi_pagination import Page
from typing_extensions import Annotated

import api.models as models
from core.db import foreign_key
from api.schemas import (
    Message,
    MessageCreate,
    MessageUpdate,
)
from api.services import get_message_service
# from api.db.schemas.filters import MessageFilter, generate_filter_query
# from api.deps import CurrentActiveUser
from api.services import MessageService

router = APIRouter(prefix="/message")

@router.get("/", response_model=Page[Message], tags=["messages"])
async def list_messages(
    message_service: Annotated[MessageService, Depends(get_message_service)],
    # message_filter: Annotated[MessageFilter, Depends()],
    # current_user: CurrentActiveUser,
) -> Page[models.Message]:
    "Get all messages"
    return message_service.get_all()


@router.get("/", response_model=Message, tags=["messages"])
async def get_random_messages(
    message_service: Annotated[MessageService, Depends(get_message_service)],
) -> models.Message:
    "Get all messages"
    return message_service.get_random()


@router.get(
    "/{message_id}",
    response_model=Message,
    responses={404: {"description": "Message not found"}},
    tags=["messages"],
)
async def get_message(
    message_id: foreign_key,
    message_service: Annotated[MessageService, Depends(get_message_service)],
    # current_user: CurrentActiveUser,
) -> Optional[Message]:
    "Get a single message by id"
    return message_service.get(message_id)


@router.post(
    "/",
    response_model=Message,
    status_code=201,
    responses={409: {"description": "Conflict Error"}},
    tags=["messages"],
)
async def create_message(
    message: MessageCreate,
    message_service: Annotated[MessageService, Depends(get_message_service)],
    # current_user: CurrentActiveUser,
) -> models.Message:
    "Create a new message"
    return message_service.create(message)


@router.patch("/{message_id}", response_model=Message, tags=["messages"])
async def update_message(
    message_id: foreign_key,
    message: MessageUpdate,
    message_service: Annotated[MessageService, Depends(get_message_service)],
    # current_user: CurrentActiveUser,
) -> Optional[models.Message]:
    return message_service.update(message_id, message)


@router.delete("/{message_id}", tags=["messages"])  # , status_code=204)
async def delete_message(
    message_id: foreign_key,
    message_service: Annotated[MessageService, Depends(get_message_service)],
    # current_user: CurrentActiveUser,
) -> Any:
    message_service.delete(message_id)
    return Response(status_code=204)