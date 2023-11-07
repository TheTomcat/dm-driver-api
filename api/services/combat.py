
from .base import BaseService, ModelType
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from api.models import Combat, Participant
from api.schemas import CombatCreate, CombatUpdate, ParticipantCreate
from typing import Any, Optional
from fastapi import HTTPException, status

class CombatService(
    BaseService[Combat, CombatCreate, CombatUpdate]
):
    def __init__(self, db_session: Session):
        super(CombatService, self).__init__(Combat, db_session)

    def add_participant_to_combat(self, combat_id: Any, participant: ParticipantCreate) -> Combat:
        combat = self.get(combat_id)
        participant = Participant(**participant.model_dump())
        combat.participants.append(participant)
        self.db_session.add(participant)
        self.db_session.commit()
        return combat

    def remove_participant_from_combat(self, combat_id: Any, participant_id: Any) -> Combat:
        combat = self.get(combat_id)
        pos = [index for index, participant in enumerate(combat.participants) if participant.id == participant_id]
        if pos:
            combat.participants.pop(pos[0])
        self.db_session.commit()
        return combat