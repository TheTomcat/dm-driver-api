import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.models import Tag
from core.services import get_tags_service

### Test SQL Mappings


def test_create_tags(db: Session) -> None:
    # t1 = Tag(label="Test", organisation_id=create_organisation.id)
    # t2 = Tag(label="Test2", organisation_id=create_organisation.id)
    db.add_all([t1, t2])
    db.commit()
    assert t1 != t2
    tags_service = get_tags_service(db)
    t3 = tags_service.get_by_label(
        "test",  # lowercase
        organisation_id=create_organisation.id,
        # create_if_nonexistant=False,
    )
    assert t3 == t1


def test_get_tags_case_insensitive(
    db: Session, create_organisation: Organisation
) -> None:
    t1 = Tag(label="Test", organisation_id=create_organisation.id)
    db.add(t1)
    db.commit()
    tags_service = get_tags_service(db)
    t3 = tags_service.get_by_label(
        "test",  # lowercase
        organisation_id=create_organisation.id,
        # create_if_nonexistant=False,
    )
    assert t3 == t1


def test_create_case_sensitive_tag(
    db: Session, create_organisation: Organisation
) -> None:
    t1 = Tag(label="Test", organisation_id=create_organisation.id)
    db.add(t1)
    db.commit()
    t2 = Tag(label="test", organisation_id=create_organisation.id)
    db.add(t2)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


# def test_create_shift_with_tagstring(
#     db: Session, create_roster: Roster, create_tag: Tag
# ) -> None:
#     d = datetime.now()
#     d1 = d + timedelta(hours=8)
#     Shift(start=d, end=d1, hours=8)


def test_tag_create(app_client: TestClient, create_organisation: Organisation) -> None:
    rv = app_client.post(
        "/tags", json={"label": "Test", "organisationId": create_organisation.id}
    )
    assert rv.status_code == 201
    assert rv.json()["id"] is not None


def test_create_child_tag(app_client: TestClient, create_tag: Tag) -> None:
    rv = app_client.post(
        "/tags",
        json={
            "label": "Test1",
            "organisationId": create_tag.organisation_id,
            "parentId": create_tag.id,
        },
    )
    assert rv.status_code == 201
    assert rv.json()["parentId"] == create_tag.id


def test_tag_shift(
    app_client: TestClient, create_shift: Shift, create_tag: Tag
) -> None:  # TODO: Finish
    payload = {"tagId": create_tag.id, "shiftId": create_shift.id, "action": "add"}
    rv = app_client.patch("/tags/shift", json=payload)
    assert rv.status_code == 200
    rv = app_client.patch("/tags/shift", json=payload)
    assert rv.status_code == 400
    payload["action"] = "remove"
    rv = app_client.patch("/tags/shift", json=payload)
    assert rv.status_code == 200


def test_tag_worker(
    app_client: TestClient, create_worker: Worker, create_tag: Tag
) -> None:  # TODO: Finish
    payload = {"tagId": create_tag.id, "workerId": create_worker.id, "action": "add"}
    rv = app_client.patch("/tags/worker", json=payload)
    assert rv.status_code == 200
    rv = app_client.patch("/tags/worker", json=payload)
    assert rv.status_code == 400
    payload["action"] = "remove"
    rv = app_client.patch("/tags/worker", json=payload)
    assert rv.status_code == 200


def test_delete(app_client: TestClient, create_shift: Shift) -> None:
    rv = app_client.get(f"/shifts/{create_shift.id}")
    assert rv.status_code == 200
    rv = app_client.delete(f"/shifts/{create_shift.id}")
    assert rv.status_code == 204
    rv = app_client.get(f"/shifts/{create_shift.id}")
    assert rv.status_code == 404


def test_update(app_client: TestClient, create_shift: Shift) -> None:
    rv = app_client.patch(
        f"/shifts/{create_shift.id}", json={"start": "2023-01-03T07:30:00"}
    )
    shift_json = rv.json()
    assert rv.status_code == 200, shift_json
    assert datetime_to_string(create_shift.start) == "2023-01-03T07:30:00"