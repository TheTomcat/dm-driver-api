from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.models import Tag
from api.schemas import TagCreate
from api.services import TagService

def test_tag_create_db(db: Session, tag_service: TagService) -> None:
    t1 = Tag(tag="test")
    t2 = Tag(tag="test2")
    db.add_all([t1, t2])
    db.commit()
    assert t1 != t2
    t3 = tag_service.get_by_name('test')
    assert t3 == t1

def test_tag_create_service(tag_service: TagService) -> None:
    t1 = tag_service.create(TagCreate(**{'tag':'Test'}))
    assert t1.tag == 'test'

def test_tag_create_case_insensitive(db: Session, tag_service: TagService) -> None:
    tagname = "Another Test"
    t1 = Tag(tag=tagname.lower()) # Lowercase
    db.add(t1)
    db.commit()
    t2 = tag_service.get_by_name(
        tagname,  # Uppercase
    )
    assert t2 == t1

def test_tag_create_client(app_client: TestClient) -> None:
    rv = app_client.post(
        "/tag", json={"tag": "Test"}
    )
    assert rv.status_code == 201
    assert rv.json()["tag_id"] is not None

def test_tag_delete_client(app_client: TestClient, create_tag: Tag) -> None:
    rv = app_client.get(f"/tag/{create_tag.id}")
    assert rv.status_code == 200
    rv = app_client.delete(f"/tag/{create_tag.id}")
    assert rv.status_code == 204
    rv = app_client.get(f"/tag/{create_tag.id}")
    assert rv.status_code == 404


def test_tag_update_client(app_client: TestClient, create_tag: Tag) -> None:
    assert create_tag.tag == create_tag.tag
    rv = app_client.patch(
        f"/tag/{create_tag.id}", json={"tag": "test1"}
    )
    tag_json = rv.json()
    assert rv.status_code == 200, tag_json
    assert create_tag.tag == "test1"

