from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.models import Combat, Participant
from api.schemas import ParticipantCreate
from api.services import ParticipantService

def test_participant_create_db(db: Session, create_combat: Combat) -> None:
    t1 = Participant(name="Test Participant 1", is_visible=True, is_PC = False, combat_id=create_combat.id,
                     damage=10, max_hp=20, ac=11, initiative=12, initiative_modifier=5, 
                     conditions='surprised', has_reaction=True, colour="#0ff00f")
    t2 = Participant(name="Test Participant 1", is_visible=True, is_PC = False, combat_id=create_combat.id,
                     damage=10, max_hp=20, ac=11, initiative=12, initiative_modifier=5, 
                     conditions='surprised', has_reaction=True, colour="#0ff00f")
    db.add_all([t1, t2])
    db.commit()
    assert t1 != t2

def test_participant_create_service(participant_service: ParticipantService, create_combat: Combat) -> None:
    t1 = participant_service.create(ParticipantCreate(**{
            "name":"Test Participant 1", "is_visible":True, "is_PC ":False, "combat_id":create_combat.id, 
            "damage":10, " max_hp":20, "ac":11, "initiative":12, "initiative_modifier":5,
            "conditions":"surprised,confused", "has_reaction":True, "colour":"#0ff00f"}))
    assert t1.name == 'Test Participant 1'

def test_participant_create_client(app_client: TestClient, create_combat: Combat) -> None:
    rv = app_client.post(
        "/participant", json={
            "name":"Test Participant 1", "is_visible":True, "is_PC ":False, "combat_id":create_combat.id, 
            "damage":10, " max_hp":20, "ac":11, "initiative":12, "initiative_modifier":5,
            "conditions":"surprised,confused", "has_reaction":True, "colour":"#0ff00f"}
    )
    assert rv.status_code == 201
    assert rv.json()["participant_id"] is not None

def test_participant_delete_client(app_client: TestClient, create_participant: Participant) -> None:
    rv = app_client.get(f"/participant/{create_participant.id}")
    assert rv.status_code == 200
    rv = app_client.delete(f"/participant/{create_participant.id}")
    assert rv.status_code == 204
    rv = app_client.get(f"/participant/{create_participant.id}")
    assert rv.status_code == 404


def test_participant_update_client(app_client: TestClient, create_participant: Participant) -> None:
    rv = app_client.patch(
        f"/participant/{create_participant.id}", json={
            "name":"Tortoise", "is_visible":True, "is_PC ":True, 
            "damage":10, "max_hp":200, "ac":11, "initiative":12, "initiative_modifier":5,
            "conditions":"surprised,confused", "has_reaction":True, "colour":"#ffffff"}
    )
    participant_json = rv.json()
    assert rv.status_code == 200, participant_json
    assert create_participant.name=="Tortoise"
    assert create_participant.max_hp==200
    assert create_participant.colour=="#ffffff"