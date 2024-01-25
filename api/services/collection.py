from typing import Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.models import Collection, image_collections
from api.schemas import CollectionCreate, CollectionUpdate

from .base import BaseService


class CollectionService(BaseService[Collection, CollectionCreate, CollectionUpdate]):
    def __init__(self, db_session: Session):
        super(CollectionService, self).__init__(Collection, db_session)

    def get_by_name(self, name: str) -> Optional[Collection]:
        collection = self.db_session.scalar(
            select(self.model).where(func.lower(self.model.name) == name.lower())
        )
        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Collection {name} not found"
            )
        return collection

    def create(self, obj: CollectionCreate) -> Collection:
        db_obj: Collection = self.model(**obj.model_dump())
        self.db_session.add(db_obj)
        try:
            self.db_session.commit()
        except IntegrityError as e:
            self.db_session.rollback()
            if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                collection = self.get_by_name(obj.name)
                if collection:
                    return collection
                raise HTTPException(status_code=409, detail=f"Conflict Error: {collection}")
            else:
                raise e
        return db_obj

    # def merge(self, merge_into_id: int, merge_from_id: int) -> None:
    #     # q = select(image_collections).where(image_collections.c.image_id == merge_from_id)
    #     q = (
    #         update(image_collections)
    #         .where(image_collections.c.collection_id == merge_from_id)
    #         .values(collection_id=merge_into_id)
    #     )
    #     self.db_session.execute(q)
    #     try:
    #         self.db_session.commit()
    #     except IntegrityError:
    #         self.db_session.rollback()
    #     print(q)
    #     # self.delete(merge_from_id)

    def get_empty_collections(self) -> Sequence[Collection]:
        q = (
            select(Collection)
            .outerjoin(image_collections, image_collections.c.collection_id == Collection.id)
            .group_by(Collection.id)
            .having(func.count(image_collections.c.image_id) == 0)
        )

        return self.db_session.scalars(q).all()
