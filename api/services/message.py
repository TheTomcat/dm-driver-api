from .base import BaseService, ModelType
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from api.models import Message
from api.schemas import MessageCreate, MessageUpdate
from typing import Optional
from fastapi import HTTPException, status


class MessageService(BaseService[Message, MessageCreate, MessageUpdate]):
    def __init__(self, db_session: Session):
        super(MessageService, self).__init__(Message, db_session)

