from typing import Any, Optional

from fastapi import APIRouter, Depends, Response
from fastapi_pagination import Page

# from fastapi_pagination.links import Page
from typing_extensions import Annotated

import api.models as models
from api.schemas import (
    Entity,
    EntityCreate,
    EntityFilter,
    EntityUpdate,
)

# from api.db.schemas.filters import EntityFilter, generate_filter_query
# from api.deps import CurrentActiveUser
from api.services import EntityService, get_entity_service
from api.utils.filters import generate_filter_query
from core.db import foreign_key

router = APIRouter(prefix="/entity")


@router.get("/", response_model=Page[Entity], tags=["entities"])
async def list_entities(
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
    entity_filter: Annotated[EntityFilter, Depends()],
    # current_user: CurrentActiveUser,
) -> Page[models.Entity]:
    "Get all entities"
    q = generate_filter_query(models.Entity, entity_filter)
    return entity_service.get_some(q)


@router.get(
    "/{entity_id}",
    response_model=Entity,
    responses={404: {"description": "Entity not found"}},
    tags=["entities"],
)
async def get_entity(
    entity_id: foreign_key,
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
    # current_user: CurrentActiveUser,
) -> models.Entity:
    "Get a single entity by id"
    return entity_service.get(entity_id)


@router.post(
    "/",
    response_model=Entity,
    status_code=201,
    responses={409: {"description": "Conflict Error"}},
    tags=["entities"],
)
async def create_entity(
    entity: EntityCreate,
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
    # current_user: CurrentActiveUser,
) -> models.Entity:
    "Create a new entity"
    return entity_service.create(entity)


@router.patch("/{entity_id}", response_model=Entity, tags=["entities"])
async def update_entity(
    entity_id: foreign_key,
    entity: EntityUpdate,
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
    # current_user: CurrentActiveUser,
) -> Optional[models.Entity]:
    return entity_service.update(entity_id, entity)


@router.delete("/{entity_id}", tags=["entities"])  # , status_code=204)
async def delete_entity(
    entity_id: foreign_key,
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
    # current_user: CurrentActiveUser,
) -> Any:
    entity_service.delete(entity_id)
    return Response(status_code=204)
