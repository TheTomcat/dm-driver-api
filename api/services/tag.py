from typing import Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.models import Tag, image_tags
from api.schemas import TagCreate, TagUpdate

from .base import BaseService


class TagService(BaseService[Tag, TagCreate, TagUpdate]):
    def __init__(self, db_session: Session):
        super(TagService, self).__init__(Tag, db_session)

    def get_by_name(self, name: str) -> Optional[Tag]:
        tag = self.db_session.scalar(
            select(self.model).where(func.lower(self.model.tag) == name.lower())
        )
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag {name} not found"
            )
        return tag

    def create(self, obj: TagCreate) -> Tag:
        db_obj: Tag = self.model(**obj.model_dump())
        self.db_session.add(db_obj)
        try:
            self.db_session.commit()
        except IntegrityError as e:
            self.db_session.rollback()
            if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                tag = self.get_by_name(obj.tag)
                if tag:
                    return tag
                raise HTTPException(status_code=409, detail=f"Conflict Error: {tag}")
            else:
                raise e
        return db_obj

    def merge(self, merge_into_id: int, merge_from_id: int) -> None:
        # q = select(image_tags).where(image_tags.c.image_id == merge_from_id)
        q = (
            update(image_tags)
            .where(image_tags.c.tag_id == merge_from_id)
            .values(tag_id=merge_into_id)
        )
        self.db_session.execute(q)
        try:
            self.db_session.commit()
        except IntegrityError:
            self.db_session.rollback()
        print(q)
        # self.delete(merge_from_id)

    def get_orphan_tags(self) -> Sequence[Tag]:
        # q = select(Tag).join(image_tags, image_tags.c.tag_id == Tag.id).where()
        # q = select(Tag, func.count(image_tags.c.image_id).label('c')).outerjoin(image_tags, image_tags.c.tag_id == Tag.id).group_by(Tag.id).where(text('c')==0)
        # q = select(Tag, func.count(image_tags.c.image_id).label('c')).outerjoin(image_tags, image_tags.c.tag_id == Tag.id).group_by(Tag.id).having(func.count(image_tags.c.image_id) == 0)
        q = (
            select(Tag)
            .outerjoin(image_tags, image_tags.c.tag_id == Tag.id)
            .group_by(Tag.id)
            .having(func.count(image_tags.c.image_id) == 0)
        )

        return self.db_session.scalars(q).all()
