from typing import Any, Optional

from fastapi import APIRouter, Depends, Response
from fastapi_pagination import Page
from typing_extensions import Annotated

import api.models as models
from api.schemas import (
    Tag,
    TagCreate,
    TagFilter,
    TagUpdate,
)

# from api.db.schemas.filters import TagFilter, generate_filter_query
# from api.deps import CurrentActiveUser
from api.services import TagService, get_tag_service
from api.utils.filters import generate_filter_query
from core.db import foreign_key

router = APIRouter(prefix="/tag")


@router.get("/", response_model=Page[Tag], tags=["tags"])
async def list_tags(
    tag_service: Annotated[TagService, Depends(get_tag_service)],
    tag_filter: Annotated[TagFilter, Depends()],
    # current_user: CurrentActiveUser,
) -> Page[models.Tag]:
    "Get all tags"
    q = generate_filter_query(models.Tag, tag_filter)
    return tag_service.get_some(q)


@router.get(
    "/{tag_id}",
    response_model=Tag,
    responses={404: {"description": "Tag not found"}},
    tags=["tags"],
)
async def get_tag(
    tag_id: foreign_key,
    tag_service: Annotated[TagService, Depends(get_tag_service)],
    # current_user: CurrentActiveUser,
) -> models.Tag:
    "Get a single tag by id"
    return tag_service.get(tag_id)


@router.post(
    "/",
    response_model=Tag,
    status_code=201,
    responses={409: {"description": "Conflict Error"}},
    tags=["tags"],
)
async def create_tag(
    tag: TagCreate,
    tag_service: Annotated[TagService, Depends(get_tag_service)],
    # current_user: CurrentActiveUser,
) -> models.Tag:
    "Create a new tag"
    return tag_service.create(tag)


@router.patch("/{tag_id}", response_model=Tag, tags=["tags"])
async def update_tag(
    tag_id: foreign_key,
    tag: TagUpdate,
    tag_service: Annotated[TagService, Depends(get_tag_service)],
    # current_user: CurrentActiveUser,
) -> Optional[models.Tag]:
    return tag_service.update(tag_id, tag)


@router.delete("/{tag_id}", tags=["tags"])  # , status_code=204)
async def delete_tag(
    tag_id: foreign_key,
    tag_service: Annotated[TagService, Depends(get_tag_service)],
    # current_user: CurrentActiveUser,
) -> Any:
    tag_service.delete(tag_id)
    return Response(status_code=204)
