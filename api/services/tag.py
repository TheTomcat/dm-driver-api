from .base import BaseService, ModelType
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from api.models import Tag
from api.schemas import TagCreate, TagUpdate
from typing import Optional
from fastapi import HTTPException, status

class TagService(
    BaseService[Tag, TagCreate, TagUpdate]
):
    def __init__(self, db_session: Session):
        super(TagService, self).__init__(Tag, db_session)
    
    def get_by_name(self, name: str) -> Optional[Tag]:
        tag = self.db_session.scalar(select(self.model).where(func.lower(self.model.tag) == name.lower()))
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag {name} not found"
            )
        return tag
