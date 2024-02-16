import json
from typing import Sequence

from fastapi import HTTPException, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models import Entity
from api.schemas import EntityCreate, EntityUpdate
from core.utils import make_seq

from .base import BaseService


class EntityService(BaseService[Entity, EntityCreate, EntityUpdate]):
    def __init__(self, db_session: Session):
        super(EntityService, self).__init__(Entity, db_session)

    async def create_from_json(self, json_file: UploadFile):
        data = await json_file.read()
        creatures = json.loads(data).get("monster", [])
        entities = []
        seq = make_seq()
        for creature in creatures:
            entities.append(Entity.from_jsondata(creature, seq))
        try:
            self.db_session.add_all(entities)
            self.db_session.commit()
        except Exception:
            self.db_session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        return Response(status_code=200)

    def get_sources(self) -> Sequence[str | None]:
        return self.db_session.scalars(select(self.model.source).distinct()).all()
