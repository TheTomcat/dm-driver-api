from typing import Any, List, Optional

from fastapi import Depends, Response, status
from fastapi.routing import APIRouter
from fastapi_pagination import Page
from typing_extensions import Annotated

import api.models as models
from core.db import foreign_key
from api.schemas import (
    Participant,
    ParticipantCreate,
    ParticipantUpdate,
)
from api.services import get_participant_service
# from api.db.schemas.filters import ParticipantFilter, generate_filter_query
# from api.deps import CurrentActiveUser
from api.services import ParticipantService

router = APIRouter(prefix="/participant")

@router.get("/", response_model=Page[Participant], tags=["participants"])
async def list_participants(
    participant_service: Annotated[ParticipantService, Depends(get_participant_service)],
    # participant_filter: Annotated[ParticipantFilter, Depends()],
    # current_user: CurrentActiveUser,
) -> Page[models.Participant]:
    "Get all participants"
    return participant_service.get_all()


@router.get(
    "/{participant_id}",
    response_model=Participant,
    responses={404: {"description": "Participant not found"}},
    tags=["participants"],
)
async def get_participant(
    participant_id: foreign_key,
    participant_service: Annotated[ParticipantService, Depends(get_participant_service)],
    # current_user: CurrentActiveUser,
) -> Optional[Participant]:
    "Get a single participant by id"
    return participant_service.get(participant_id)


@router.post(
    "/",
    response_model=Participant,
    status_code=201,
    responses={409: {"description": "Conflict Error"}},
    tags=["participants"],
)
async def create_participant(
    participant: ParticipantCreate,
    participant_service: Annotated[ParticipantService, Depends(get_participant_service)],
    # current_user: CurrentActiveUser,
) -> models.Participant:
    "Create a new participant"
    return participant_service.create(participant)


@router.patch("/{participant_id}", response_model=Participant, tags=["participants"])
async def update_participant(
    participant_id: foreign_key,
    participant: ParticipantUpdate,
    participant_service: Annotated[ParticipantService, Depends(get_participant_service)],
    # current_user: CurrentActiveUser,
) -> Optional[models.Participant]:
    return participant_service.update(participant_id, participant)


@router.delete("/{participant_id}", tags=["participants"])  # , status_code=204)
async def delete_participant(
    participant_id: foreign_key,
    participant_service: Annotated[ParticipantService, Depends(get_participant_service)],
    # current_user: CurrentActiveUser,
) -> Any:
    participant_service.delete(participant_id)
    return Response(status_code=204)