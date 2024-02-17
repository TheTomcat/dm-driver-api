from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from core.session import get_session

from .collection import CollectionService
from .combat import CombatService
from .entity import EntityService
from .image import ImageService
from .message import MessageService
from .participant import ParticipantService
from .rolltable import RollTableRowService, RollTableService
from .tag import TagService

# from .session import SessionService


def get_tag_service(db_session: Annotated[Session, Depends(get_session)]) -> TagService:
    return TagService(db_session)


def get_image_service(db_session: Annotated[Session, Depends(get_session)]) -> ImageService:
    return ImageService(db_session)


def get_message_service(db_session: Annotated[Session, Depends(get_session)]) -> MessageService:
    return MessageService(db_session)


def get_combat_service(db_session: Annotated[Session, Depends(get_session)]) -> CombatService:
    return CombatService(db_session)


def get_participant_service(
    db_session: Annotated[Session, Depends(get_session)]
) -> ParticipantService:
    return ParticipantService(db_session)


def get_entity_service(db_session: Annotated[Session, Depends(get_session)]) -> EntityService:
    return EntityService(db_session)


def get_collection_service(
    db_session: Annotated[Session, Depends(get_session)]
) -> CollectionService:
    return CollectionService(db_session)


def get_rolltable_service(db_session: Annotated[Session, Depends(get_session)]) -> RollTableService:
    return RollTableService(db_session)


def get_rolltable_row_service(
    db_session: Annotated[Session, Depends(get_session)]
) -> RollTableRowService:
    return RollTableRowService(db_session)
