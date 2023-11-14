from sqlalchemy.orm import Session

from api.models import Participant
from api.schemas import ParticipantCreate, ParticipantUpdate

from .base import BaseService


class ParticipantService(BaseService[Participant, ParticipantCreate, ParticipantUpdate]):
    def __init__(self, db_session: Session):
        super(ParticipantService, self).__init__(Participant, db_session)
