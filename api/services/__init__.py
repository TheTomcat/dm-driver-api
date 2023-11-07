from typing import Annotated
from fastapi import Depends
from core.session import get_session
from sqlalchemy.orm import Session
from .tag import TagService
from .image import ImageService
from .message import MessageService
from .session import SessionService 
from .combat import CombatService
from .participant import ParticipantService
from .entity import EntityService

def get_tag_service(
    db_session: Annotated[Session, Depends(get_session)]
) -> TagService:
    return TagService(db_session)

def get_image_service(
    db_session: Annotated[Session, Depends(get_session)]
) -> ImageService:
    return ImageService(db_session)

def get_message_service(
    db_session: Annotated[Session, Depends(get_session)]
) -> MessageService:
    return MessageService(db_session)

def get_session_service(
    db_session: Annotated[Session, Depends(get_session)]
) -> SessionService:
    return SessionService(db_session)

def get_combat_service(
    db_session: Annotated[Session, Depends(get_session)]
) -> CombatService:
    return CombatService(db_session)

def get_participant_service(
    db_session: Annotated[Session, Depends(get_session)]
) -> ParticipantService:
    return ParticipantService(db_session)

def get_entity_service(
    db_session: Annotated[Session, Depends(get_session)]
) -> EntityService:
    return EntityService(db_session)