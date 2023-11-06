from typing import Any, Generic, Optional, Type, TypeVar

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel
from sqlalchemy import Select, delete, select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from core.db import Base
from api.models import (Directory, Image, Tag, Message)
from api.schemas import DirectoryCreate, DirectoryUpdate, ImageCreate, ImageUpdate, TagCreate, TagUpdate, MessageCreate, MessageUpdate

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db_session: Session):
        self.model = model
        self.db_session = db_session

    def get(self, id: Any) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        obj: Optional[ModelType] = self.db_session.scalar(query)
        if obj is None:
            raise HTTPException(status_code=404, detail="Not Found")
        return obj

    def get_all(self) -> Page[ModelType]:
        query = select(self.model)
        return paginate(self.db_session, query)

    def get_some(self, q: Select) -> Page[ModelType]:
        return paginate(self.db_session, q)
    
    def get_random(self) -> Page[ModelType]:
        return select(self.model).order_by(func.random())

    def create(self, obj: CreateSchemaType) -> ModelType:
        db_obj: ModelType = self.model(**obj.model_dump())
        self.db_session.add(db_obj)
        try:
            self.db_session.commit()
        except IntegrityError as e:
            self.db_session.rollback()
            if "duplicate key" in str(e):
                raise HTTPException(status_code=409, detail="Conflict Error")
            else:
                raise e
        return db_obj

    def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        db_obj = self.get(id)
        for column, value in obj.model_dump(exclude_unset=True).items():
            setattr(db_obj, column, value)
        self.db_session.commit()
        return db_obj

    def delete(self, id: Any) -> None:
        query = delete(self.model).where(self.model.id == id)
        self.db_session.execute(query)
        self.db_session.commit()


############## Image

class ImageService(
    BaseService[Image, ImageCreate, ImageUpdate]
):
    def __init__(self, db_session: Session):
        super(ImageService, self).__init__(Image, db_session)

class DirectoryService(
    BaseService[Directory, DirectoryCreate, DirectoryUpdate]
):
    def __init__(self, db_session: Session):
        super(DirectoryService, self).__init__(Directory, db_session)

class TagService(
    BaseService[Tag, TagCreate, TagUpdate]
):
    def __init__(self, db_session: Session):
        super(TagService, self).__init__(Tag, db_session)
    
    def get_by_name(self, name: str) -> Optional[ModelType]:
        tag = self.db_session.scalar(select(self.model).where(self.model.name == name.lower()))
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag {name} not found"
            )
        return tag


class MessageService(BaseService[Message, MessageCreate, MessageUpdate]):
    def __init__(self, db_session: Session):
        super(MessageService, self).__init__(Message, db_session)

class SessionService():
    pass

class CombatService():
    pass

class EntityService():
    pass

class ParticipantService():
    pass