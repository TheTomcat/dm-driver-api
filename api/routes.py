from typing import Any, List, Optional

from fastapi import Depends, Response, status
from fastapi.routing import APIRouter
from fastapi_pagination import Page
from typing_extensions import Annotated

import api.models as models
from core.db import foreign_key
from api.schemas import (
    Tag,
    TagCreate,
    TagUpdate,
)
# from api.db.schemas.filters import TagFilter, generate_filter_query
# from api.deps import CurrentActiveUser
from core.services import TagService

tags_router = APIRouter(prefix="/tags")


# @tags_router.get("/", response_model=Page[Tag], tags=["tags"])
# async def list_tags(
#     tag_service: TagService,
#     # tag_filter: Annotated[TagFilter, Depends()],
#     # current_user: CurrentActiveUser,
# ) -> Page[models.Tag]:
#     "Get all tags"
#     return tag_service.get_all()


@tags_router.get(
    "/{tag_id}",
    response_model=Tag,
    responses={404: {"description": "Tag not found"}},
    tags=["tags"],
)
async def get_tag(
    tag_id: foreign_key,
    tag_service: TagService,
    # current_user: CurrentActiveUser,
) -> Optional[models.Tag]:
    "Get a single tag by id"
    return tag_service.get(tag_id)


@tags_router.get(
    "/{tag_id}",
    response_model=List[Tag],
    responses={404: {"description": "Tag not found"}},
    tags=["tags"],
)
async def get_tag_tree(
    tag_id: foreign_key,
    tag_service: TagService,
    # current_user: CurrentActiveUser,
) -> Optional[List[models.Tag]]:
    "Return a flat list of all child tags, recursively"
    return tag_service.get_all_child_tags(tag_id)


@tags_router.post(
    "/",
    response_model=Tag,
    status_code=201,
    responses={409: {"description": "Conflict Error"}},
    tags=["tags"],
)
async def create_tag(
    tag: TagCreate,
    tag_service: TagService,
    # current_user: CurrentActiveUser,
) -> models.Tag:
    "Create a new tag"
    return tag_service.create(tag)


@tags_router.patch("/{tag_id}", response_model=Tag, tags=["tags"])
async def update_tag(
    tag_id: foreign_key,
    tag: TagUpdate,
    tag_service: TagService,
    # current_user: CurrentActiveUser,
) -> Optional[models.Tag]:
    return tag_service.update(tag_id, tag)


@tags_router.delete("/{tag_id}", tags=["tags"])  # , status_code=204)
async def delete_tag(
    tag_id: foreign_key,
    tag_service: TagService,
    # current_user: CurrentActiveUser,
) -> Any:
    tag_service.delete(tag_id)
    return Response(status_code=204)