from typing import Any, List, Optional

from fastapi import Depends, Response, status
from fastapi.routing import APIRouter
from fastapi_pagination import Page
from typing_extensions import Annotated

import api.models as models
from core.db import foreign_key
from api.schemas import (
    Combat,
    CombatCreate,
    CombatUpdate,
    ParticipantCreate,
)
from api.services import get_combat_service
# from api.db.schemas.filters import CombatFilter, generate_filter_query
# from api.deps import CurrentActiveUser
from api.services import CombatService

router = APIRouter(prefix="/combat")

@router.get("/", response_model=Page[Combat], tags=["combats"])
async def list_combats(
    combat_service: Annotated[CombatService, Depends(get_combat_service)],
    # combat_filter: Annotated[CombatFilter, Depends()],
    # current_user: CurrentActiveUser,
) -> Page[models.Combat]:
    "Get all combats"
    return combat_service.get_all()


@router.get(
    "/{combat_id}",
    response_model=Combat,
    responses={404: {"description": "Combat not found"}},
    tags=["combats"],
)
async def get_combat(
    combat_id: foreign_key,
    combat_service: Annotated[CombatService, Depends(get_combat_service)],
    # current_user: CurrentActiveUser,
) -> Optional[Combat]:
    "Get a single combat by id"
    return combat_service.get(combat_id)


@router.post(
    "/",
    response_model=Combat,
    status_code=201,
    responses={409: {"description": "Conflict Error"}},
    tags=["combats"],
)
async def create_combat(
    combat: CombatCreate,
    combat_service: Annotated[CombatService, Depends(get_combat_service)],
    # current_user: CurrentActiveUser,
) -> models.Combat:
    "Create a new combat"
    return combat_service.create(combat)


@router.patch("/{combat_id}", response_model=Combat, tags=["combats"])
async def update_combat(
    combat_id: foreign_key,
    combat: CombatUpdate,
    combat_service: Annotated[CombatService, Depends(get_combat_service)],
    # current_user: CurrentActiveUser,
) -> Optional[models.Combat]:
    return combat_service.update(combat_id, combat)


@router.delete("/{combat_id}", tags=["combats"])  # , status_code=204)
async def delete_combat(
    combat_id: foreign_key,
    combat_service: Annotated[CombatService, Depends(get_combat_service)],
    # current_user: CurrentActiveUser,
) -> Any:
    combat_service.delete(combat_id)
    return Response(status_code=204)

@router.patch("/{combat_id}/add", tags=["combats"])
async def add_participant_to_combat(
    combat_id: foreign_key,
    participant: ParticipantCreate,
    combat_service: Annotated[CombatService, Depends(get_combat_service)],
    # current_user: CurrentActiveUser,
) -> Combat:
    return combat_service.add_participant_to_combat(combat_id, participant)

@router.patch("/{combat_id}/remove", tags=["combats"])
async def remove_participant_from_combat(
    combat_id: foreign_key,
    participant_id: foreign_key,
    combat_service: Annotated[CombatService, Depends(get_combat_service)],
    # current_user: CurrentActiveUser,
) -> Combat:
    return combat_service.remove_participant_from_combat(combat_id, participant_id)