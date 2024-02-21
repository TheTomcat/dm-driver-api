from typing import Any, Optional

from fastapi import APIRouter, Depends, Response
from fastapi_pagination import Page
from sqlalchemy import select
from typing_extensions import Annotated

import api.models as models
from api.schemas import RollTableCreate, RollTableDB, RollTableRowCreateInTable, RollTableUpdate

# from api.db.schemas.filters import RollTableFilter, generate_filter_query
# from api.deps import CurrentActiveUser
from api.services import RollTableService, get_rolltable_service
from core.db import foreign_key

router = APIRouter(prefix="/rolltable")


@router.get("/", response_model=Page[RollTableDB], tags=["rolltables"])
async def list_rolltables(
    rolltable_service: Annotated[RollTableService, Depends(get_rolltable_service)],
    # rolltable_filter: Annotated[RollTableFilter, Depends()],
    # current_user: CurrentActiveUser,
) -> Page[models.RollTable]:
    "Get all rolltables"
    # q = generate_filter_query(models.RollTable, rolltable_filter)
    q = select(models.RollTable)
    return rolltable_service.get_some(q)  # , transformer=build_transformer(router))


# @router.get("/orphans", tags=["rolltables"])
# async def get_empty_rolltables(
#     rolltable_service: Annotated[RollTableService, Depends(get_rolltable_service)]
# ) -> Sequence[RollTable]:
#     return rolltable_service.get_empty_rolltables()  # type: ignore


@router.get(
    "/{rolltable_id}",
    response_model=RollTableDB,
    responses={404: {"description": "RollTable not found"}},
    tags=["rolltables"],
)
async def get_rolltable(
    rolltable_id: foreign_key,
    rolltable_service: Annotated[RollTableService, Depends(get_rolltable_service)],
    # current_user: CurrentActiveUser,
) -> models.RollTable:
    "Get a single rolltable by id"
    return rolltable_service.get(rolltable_id)


@router.post(
    "/",
    response_model=RollTableDB,
    status_code=201,
    responses={409: {"description": "Conflict Error"}},
    tags=["rolltables"],
)
async def create_rolltable(
    rolltable: RollTableCreate,
    rolltable_service: Annotated[RollTableService, Depends(get_rolltable_service)],
    # current_user: CurrentActiveUser,
) -> models.RollTable:
    "Create a new rolltable"
    return rolltable_service.create(rolltable)


@router.delete("/{rolltable_id}", tags=["rolltables"])  # , status_code=204)
async def delete_rolltable(
    rolltable_id: foreign_key,
    rolltable_service: Annotated[RollTableService, Depends(get_rolltable_service)],
    # current_user: CurrentActiveUser,
) -> Any:
    rolltable_service.delete(rolltable_id)
    return Response(status_code=204)


@router.patch("/{rolltable_id}", response_model=RollTableDB, tags=["rolltables"])
async def update_rolltable(
    rolltable_id: foreign_key,
    rolltable: RollTableUpdate,
    rolltable_service: Annotated[RollTableService, Depends(get_rolltable_service)],
    # current_user: CurrentActiveUser,
) -> Optional[models.RollTable]:
    return rolltable_service.update(rolltable_id, rolltable)


@router.post("/{rolltable_id}/row/add", response_model=RollTableDB, tags=["rolltables"])
async def create_row_on_rolltable(
    rolltable_id: foreign_key,
    rolltable_row: RollTableRowCreateInTable,
    rolltable_service: Annotated[RollTableService, Depends(get_rolltable_service)],
) -> models.RollTable:
    return rolltable_service.add_row_to_table(rolltable_id, rolltable_row)


@router.delete("/row/{rolltable_row_id}/remove", response_model=RollTableDB, tags=["rolltables"])
async def delete_row_from_rolltable(
    rolltable_row_id: foreign_key,
    rolltable_service: Annotated[RollTableService, Depends(get_rolltable_service)],
):
    rolltable_service.delete(rolltable_row_id)
    return Response(status_code=204)
