from sqlalchemy.orm import Session

from api.models import Entity
from api.schemas import EntityCreate, EntityUpdate

from .base import BaseService


class EntityService(BaseService[Entity, EntityCreate, EntityUpdate]):
    def __init__(self, db_session: Session):
        super(EntityService, self).__init__(Entity, db_session)
