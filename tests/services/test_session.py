from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as DBSession

from api.models import Image, Message, Session
from api.schemas import SessionCreate
from api.services import SessionService


def test_session_create_db(db: DBSession) -> None:
    t1 = Session(title="Player Screen 1")
    t2 = Session(title="Someone chilling at home")
    db.add_all([t1, t2])
    db.flush()
    assert t1 != t2


def test_session_create_service(session_service: SessionService) -> None:
    t1 = session_service.create(SessionCreate(**{"title": "Player Screen 1"}))  # type: ignore
    assert t1.title == "Player Screen 1"


def test_session_client_create_empty(app_client: TestClient) -> None:
    title = "An empty session, without mode specified."
    rv = app_client.post("/session", json={"title": title})
    assert rv.status_code == 201, rv.text
    assert rv.json()["session_id"] is not None
    assert rv.json()["mode"] == "empty"
    assert rv.json()["title"] == title


def test_session_client_create_empty_2(app_client: TestClient) -> None:
    title = "An empty session, with mode specified as empty"
    rv = app_client.post("/session", json={"title": title, "mode": "empty"})
    assert rv.status_code == 201, rv.text
    assert rv.json()["session_id"] is not None
    assert rv.json()["mode"] == "empty"
    assert rv.json()["title"] == title


def test_session_client_create_invalid_mode(app_client: TestClient) -> None:
    title = "An empty session, with an invalid mode specified"
    rv = app_client.post("/session", json={"title": title, "mode": "not a mode"})
    assert rv.status_code == 422
    assert "literal_error" in rv.text


def test_session_client_create_backdrop(app_client: TestClient, create_image: Image) -> None:
    title = "A valid backdrop session"
    rv = app_client.post(
        "/session", json={"title": title, "mode": "backdrop", "backdrop_id": create_image.id}
    )
    assert rv.status_code == 201
    assert rv.json()["mode"] == "backdrop"


def test_session_client_create_loading(
    app_client: TestClient, create_image: Image, create_message: Message
) -> None:
    title = "A valid backdrop session"
    rv = app_client.post(
        "/session", json={"title": title, "mode": "backdrop", "backdrop_id": create_image.id}
    )
    assert rv.status_code == 201
    assert rv.json()["mode"] == "backdrop"


def test_client_delete(app_client: TestClient, create_session: Session) -> None:
    rv = app_client.get(f"/session/{create_session.id}")
    assert rv.status_code == 200
    rv = app_client.delete(f"/session/{create_session.id}")
    assert rv.status_code == 204
    rv = app_client.get(f"/session/{create_session.id}")
    assert rv.status_code == 404


def test_client_update(
    app_client: TestClient, create_session: Session, create_image: Image
) -> None:
    rv = app_client.patch(
        f"/session/{create_session.id}",
        json={"title": "Another test", "backdrop_id": create_image.id},
    )
    session_json = rv.json()
    assert rv.status_code == 200, session_json
    assert session_json["title"] == "Another test"
    assert (
        session_json["backdrop_id"] == 1
    )  # For some reason, create_image.id is unbound at this point... No idea why.


# Test session modes have appropriate fields
# class SessionMode(enum.Enum):
#     loading = "loading"
#     backdrop = "backdrop"
#     combat = "combat"
#     handout = "handout"
#     map = "map"


def test_session_mode_backdrop(app_client: TestClient, create_session: Session):
    pass


# def test_session_mode_loading(app_client: TestClient):
#     rv = app_client.post("/session/", json={"title": "A session."})

#     rv = app_client.patch(f"/session/{sid1}", json={"mode": "loading"})
#     assert rv.status_code == 200
#     assert rv.json()["mode"] == "loading"
#     # rv = app_client.get(f"/session/{create_session.id}")  # this isn't necessary but oh well
#     # assert rv.status_code == 200
#     payload = rv.json()
#     assert "mode" in payload
#     assert payload["mode"] == "loading"
#     assert "backdrop" in payload
#     assert "backdrop_id" in payload
#     # with pytest.raises(fastapi.exceptions.ResponseValidationError):
#     rv = app_client.patch(f"/session/{sid2}", json={"mode": "loading"})
#     assert rv.status_code == 200
#     assert rv.json()["mode"] == "loading"


def test_session_mode_combat(app_client: TestClient, create_session: Session):
    pass


def test_session_mode_handout(app_client: TestClient, create_session: Session):
    pass


def test_session_mode_map(app_client: TestClient, create_session: Session):
    pass
