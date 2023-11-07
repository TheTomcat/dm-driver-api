from typing import Any, Generic, Optional, Type, TypeVar, Annotated

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel
from sqlalchemy import Select, delete, select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends

from core.db import Base


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

