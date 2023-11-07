from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.models import Message
from api.schemas import MessageCreate
from api.services import MessageService

def test_message_create(db: Session, message_service: MessageService) -> None:
    t1 = Message(message="A new and lengthy message")
    t2 = Message(message="Another new, lengthy and witty message")
    db.add_all([t1, t2])
    db.commit()
    assert t1 != t2

def test_create(message_service: MessageService) -> None:
    t1 = message_service.create(MessageCreate(**{'message':'A wonderfully witty and funny message'}))
    assert t1.message == 'A wonderfully witty and funny message'

def test_client_message_create(app_client: TestClient) -> None:
    rv = app_client.post(
        "/messages", json={"message": "A third and hilarious message."}
    )
    assert rv.status_code == 201
    assert rv.json()["message_id"] is not None

def test_client_delete(app_client: TestClient, create_message: Message) -> None:
    rv = app_client.get(f"/messages/{create_message.id}")
    assert rv.status_code == 200
    rv = app_client.delete(f"/messages/{create_message.id}")
    assert rv.status_code == 204
    rv = app_client.get(f"/messages/{create_message.id}")
    assert rv.status_code == 404


def test_client_update(app_client: TestClient, create_message: Message) -> None:
    assert create_message.message == create_message.message
    rv = app_client.patch(
        f"/messages/{create_message.id}", json={"message": "test1"}
    )
    message_json = rv.json()
    assert rv.status_code == 200, message_json
    assert create_message.message == "test1"


def test_message_id_mapping(db: Session, message_service: MessageService, app_client: TestClient, create_message: Message) -> None:
    pass

