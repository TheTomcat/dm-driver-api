from .base import BaseService
from sqlalchemy.orm import Session as DBSession
from api.models import Session
from api.schemas import SessionCreate, SessionUpdate

class SessionService(
    BaseService[Session, SessionCreate, SessionUpdate]
):
    def __init__(self, db_session: DBSession):
        super(SessionService, self).__init__(Session, db_session)

