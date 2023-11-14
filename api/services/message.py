from sqlalchemy.orm import Session

from api.models import Message
from api.schemas import MessageCreate, MessageUpdate

from .base import BaseService


class MessageService(BaseService[Message, MessageCreate, MessageUpdate]):
    def __init__(self, db_session: Session):
        super(MessageService, self).__init__(Message, db_session)
