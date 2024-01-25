from typing import Any, Optional, Sequence

from fastapi import APIRouter, Depends, Response
from fastapi_pagination import Page
from typing_extensions import Annotated

import api.models as models
from api.schemas import (
    Collection,
    CollectionCreate,
    CollectionFilter,
    CollectionUpdate,
)

# from api.db.schemas.filters import CollectionFilter, generate_filter_query
# from api.deps import CurrentActiveUser
from api.services import CollectionService, get_collection_service
from api.utils.filters import generate_filter_query
from core.db import foreign_key

router = APIRouter(prefix="/collection")


@router.get("/", response_model=Page[Collection], tags=["collections"])
async def list_collections(
    collection_service: Annotated[CollectionService, Depends(get_collection_service)],
    collection_filter: Annotated[CollectionFilter, Depends()],
    # current_user: CurrentActiveUser,
) -> Page[models.Collection]:
    "Get all collections"
    q = generate_filter_query(models.Collection, collection_filter)
    return collection_service.get_some(q)  # , transformer=build_transformer(router))


@router.get("/orphans", tags=["collections"])
async def get_empty_collections(
    collection_service: Annotated[CollectionService, Depends(get_collection_service)]
) -> Sequence[Collection]:
    return collection_service.get_empty_collections()  # type: ignore


@router.get(
    "/{collection_id}",
    response_model=Collection,
    responses={404: {"description": "Collection not found"}},
    tags=["collections"],
)
async def get_collection(
    collection_id: foreign_key,
    collection_service: Annotated[CollectionService, Depends(get_collection_service)],
    # current_user: CurrentActiveUser,
) -> models.Collection:
    "Get a single collection by id"
    return collection_service.get(collection_id)


@router.post(
    "/",
    response_model=Collection,
    status_code=201,
    responses={409: {"description": "Conflict Error"}},
    tags=["collections"],
)
async def create_collection(
    collection: CollectionCreate,
    collection_service: Annotated[CollectionService, Depends(get_collection_service)],
    # current_user: CurrentActiveUser,
) -> models.Collection:
    "Create a new collection"
    return collection_service.create(collection)


@router.patch("/{collection_id}", response_model=Collection, tags=["collections"])
async def update_collection(
    collection_id: foreign_key,
    collection: CollectionUpdate,
    collection_service: Annotated[CollectionService, Depends(get_collection_service)],
    # current_user: CurrentActiveUser,
) -> Optional[models.Collection]:
    return collection_service.update(collection_id, collection)


@router.delete("/{collection_id}", tags=["collections"])  # , status_code=204)
async def delete_collection(
    collection_id: foreign_key,
    collection_service: Annotated[CollectionService, Depends(get_collection_service)],
    # current_user: CurrentActiveUser,
) -> Any:
    collection_service.delete(collection_id)
    return Response(status_code=204)
