from sqlalchemy.orm import Session as DBSession

from api.models import Session
from api.schemas import SessionCreate, SessionUpdate

from .base import BaseService


class SessionService(BaseService[Session, SessionCreate, SessionUpdate]):
    def __init__(self, db_session: DBSession):
        super(SessionService, self).__init__(Session, db_session)

    # def create(self, obj: SessionCreate) -> Session:
    #     print("Creating")
    #     db_obj: Session = self.model(**obj.model_dump())
    #     self.db_session.add(db_obj)
    #     try:
    #         self.db_session.commit()
    #     except IntegrityError as e:
    #         self.db_session.rollback()
    #         if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
    #             raise HTTPException(status_code=409, detail="Conflict Error")
    #         else:
    #             raise e
    #     return db_obj

    # def update(self, id: Any, obj: SessionUpdate) -> Optional[Session]:
    #     db_obj = self.get(id)
    #     for column, value in obj.model_dump(exclude_unset=True).items():
    #         setattr(db_obj, column, value)
    #     try:
    #         self.db_session.commit()
    #     except IntegrityError as e:
    #         self.db_session.rollback()
    #         if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
    #             raise HTTPException(status_code=409, detail="Conflict Error")
    #         else:
    #             raise e
    #     return db_obj

    # def set_mode(self, session_id: int, mode: SessionMode) -> Session:
    #     session = self.get(session_id)
    #     session.mode = mode
    #     self.db_session.commit()
    #     return session
