
from .base import BaseService, ModelType
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from api.models import Participant
from api.schemas import ParticipantCreate, ParticipantUpdate
from typing import Optional
from fastapi import HTTPException, status

class ParticipantService(
    BaseService[Participant, ParticipantCreate, ParticipantUpdate]
):
    def __init__(self, db_session: Session):
        super(ParticipantService, self).__init__(Participant, db_session)

