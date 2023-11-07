
from .base import BaseService, ModelType
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from api.models import Entity
from api.schemas import EntityCreate, EntityUpdate
from typing import Optional
from fastapi import HTTPException, status

class EntityService(
    BaseService[Entity, EntityCreate, EntityUpdate]
):
    def __init__(self, db_session: Session):
        super(EntityService, self).__init__(Entity, db_session)




