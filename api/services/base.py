from typing import Any, Generic, Optional, Type, TypeVar

from fastapi import HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel
from sqlalchemy import Select, delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.db import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db_session: Session):
        self.model = model
        self.db_session = db_session

    def get(self, id: Any) -> ModelType:
        query = select(self.model).where(self.model.id == id)
        obj: Optional[ModelType] = self.db_session.scalar(query)
        if obj is None:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} Not Found")
        return obj

    def get_all(self) -> Page[ModelType]:
        query = select(self.model)  # .order_by(self.model.id.desc())
        return paginate(self.db_session, query)

    def get_some(self, q: Optional[Select] = None, transformer=None) -> Page[ModelType]:
        if q is None:
            q = select(self.model)
        return paginate(self.db_session, q, transformer=transformer)

    def get_random(self) -> ModelType:
        # return self.db_session.scalar(select(Image).where(*conditions).order_by(func.random()))
        q = select(self.model).order_by(func.random())
        obj: Optional[ModelType] = self.db_session.scalar(q)
        if obj is None:
            raise HTTPException(status_code=404, detail=f"{ModelType.__name__} Not Found")
        return obj

    def create(self, obj: CreateSchemaType) -> ModelType:
        db_obj: ModelType = self.model(**obj.model_dump())
        self.db_session.add(db_obj)
        try:
            self.db_session.commit()
        except IntegrityError as e:
            self.db_session.rollback()
            if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                raise HTTPException(status_code=409, detail="Conflict Error")
            else:
                raise e
        return db_obj

    def update(self, id: Any, obj: UpdateSchemaType) -> ModelType:
        db_obj = self.get(id)
        for column, value in obj.model_dump(exclude_unset=True).items():
            setattr(db_obj, column, value)
        try:
            self.db_session.commit()
        except IntegrityError as e:
            self.db_session.rollback()
            if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                raise HTTPException(status_code=409, detail="Conflict Error")
            else:
                raise e
        return db_obj

    def replace(self, id: Any, obj: UpdateSchemaType) -> ModelType:
        raise NotImplementedError("This is not yet implemented")
        db_obj = self.get(id)
        for column, value in obj.model_dump(exclude_unset=True).items():
            setattr(db_obj, column, value)
        try:
            self.db_session.commit()
        except IntegrityError as e:
            self.db_session.rollback()
            if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                raise HTTPException(status_code=409, detail="Conflict Error")
            else:
                raise e
        return db_obj

    def delete(self, id: Any) -> None:
        query = delete(self.model).where(self.model.id == id)
        try:
            self.db_session.execute(query)
            self.db_session.commit()
        except IntegrityError:
            self.db_session.rollback()
