from typing import Any, Optional

from fastapi import APIRouter, Depends, Response
from fastapi_pagination import Page
from typing_extensions import Annotated

import api.models as models
from api.schemas import (
    Combat,
    CombatCreate,
    CombatFilter,
    CombatSortBy,
    CombatUpdate,
    ParticipantCreate,
)

# from api.db.schemas.filters import CombatFilter, generate_filter_query
# from api.deps import CurrentActiveUser
from api.services import CombatService, get_combat_service
from api.utils.filters import generate_filter_query, generate_sort_query
from core.db import foreign_key

# router = HandleTrailingSlashRouter(prefix="/combat")
router = APIRouter(prefix="/combat")


@router.get("/", response_model=Page[Combat], tags=["combats"])
async def list_combats(
    combat_service: Annotated[CombatService, Depends(get_combat_service)],
    combat_filter: Annotated[CombatFilter, Depends()],
    sort_by: Annotated[CombatSortBy, Depends()],
    # current_user: CurrentActiveUser,
) -> Page[models.Combat]:
    "Get all combats"

    q = generate_filter_query(models.Combat, combat_filter)  # .order_by(models.Combat.id.desc())
    q = generate_sort_query(q, models.Combat, sort_by)
    # print(combat_filter)
    return combat_service.get_some(q)


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
) -> Optional[models.Combat]:
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
) -> Optional[models.Combat]:
    "Create a new combat"
    return combat_service.create(combat)


@router.patch("/{combat_id}", response_model=Combat, tags=["combats"])
async def update_combat(
    combat_id: foreign_key,
    combat: CombatUpdate,
    combat_service: Annotated[CombatService, Depends(get_combat_service)],
    # current_user: CurrentActiveUser,
) -> models.Combat:
    return combat_service.update(combat_id, combat)


@router.delete("/{combat_id}", tags=["combats"])  # , status_code=204)
async def delete_combat(
    combat_id: foreign_key,
    combat_service: Annotated[CombatService, Depends(get_combat_service)],
    # current_user: CurrentActiveUser,
) -> Any:
    combat_service.delete(combat_id)
    return Response(status_code=204)


@router.patch("/{combat_id}/add", response_model=Combat, tags=["combats"])
async def add_participant_to_combat(
    combat_id: foreign_key,
    participants: list[ParticipantCreate],
    combat_service: Annotated[CombatService, Depends(get_combat_service)],
    # current_user: CurrentActiveUser,
) -> Optional[models.Combat]:
    return combat_service.add_participant_to_combat(combat_id, participants)


@router.delete("/{combat_id}/remove", tags=["combats"], response_model=Combat)
async def remove_participant_from_combat(
    combat_id: foreign_key,
    participant_id: foreign_key,
    combat_service: Annotated[CombatService, Depends(get_combat_service)],
    # current_user: CurrentActiveUser,
) -> Optional[models.Combat]:
    return combat_service.remove_participant_from_combat(combat_id, participant_id)
