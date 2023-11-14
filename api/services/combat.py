from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.models import Combat, Participant
from api.schemas import CombatCreate, CombatUpdate, ParticipantCreate

from .base import BaseService


class CombatService(BaseService[Combat, CombatCreate, CombatUpdate]):
    def __init__(self, db_session: Session):
        super(CombatService, self).__init__(Combat, db_session)

    def create(self, combat: CombatCreate) -> Combat:
        combat_obj = Combat(title=combat.title)
        participants = combat.participants
        if participants is not None:
            combat_obj.participants.extend(Participant(**p.model_dump()) for p in participants)
        self.db_session.add(combat_obj)
        try:
            self.db_session.commit()
        except IntegrityError as e:
            self.db_session.rollback()
            if "duplicate key" in str(e):
                raise HTTPException(status_code=409, detail="Conflict Error")
            else:
                raise e
        return combat_obj

    def add_participant_to_combat(
        self, combat_id: Any, participants: list[ParticipantCreate]
    ) -> Combat:
        combat = self.get(combat_id)
        if not combat:
            # return Response(status_code=404)
            raise HTTPException(status_code=404)
        try:
            for participant in participants:
                participant_model = Participant(**participant.model_dump())
                combat.participants.append(participant_model)
                self.db_session.add(participant_model)
        except Exception:
            self.db_session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        self.db_session.commit()
        return combat

    def remove_participant_from_combat(self, combat_id: Any, participant_id: Any) -> Combat:
        combat = self.get(combat_id)
        if not combat:
            raise HTTPException(status_code=404)
            # return Response(status_code=404)
        pos = [
            index
            for index, participant in enumerate(combat.participants)
            if participant.id == participant_id
        ]
        if pos:
            combat.participants.pop(pos[0])
        self.db_session.commit()
        return combat

    def update(self, id: Any, obj: CombatUpdate) -> Combat:
        # participant_service = get_participant_service(self.db_session)
        db_obj = self.get(id)
        model_dump = obj.model_dump(exclude_unset=True)
        for column, value in model_dump.items():
            if column == "participants":
                try:
                    for participant in model_dump[column]:
                        # participant_service.update(participant['id'], participant)
                        participant_obj = self.db_session.scalar(
                            select(Participant).where(Participant.id == participant["id"])
                        )
                        for col, v in participant.items():
                            if col == "id":
                                continue
                            setattr(participant_obj, col, v)
                except Exception as e:
                    raise e
            else:
                setattr(db_obj, column, value)
        try:
            self.db_session.commit()
        except IntegrityError as e:
            self.db_session.rollback()
            if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                raise HTTPException(status_code=409, detail="Conflict Error")
            else:
                raise e
        return db_obj
