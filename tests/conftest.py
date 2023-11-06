import os
from datetime import date, datetime
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from api.api import create_app
# from api.db.models import Base, Organisation, Roster, Shift, Tag, Worker
from core.session import get_session
from core.db import Base


@pytest.fixture(scope="session")
def db() -> Generator[Session, None, None]:
    SQLALCHEMY_DATABASE_URL = os.environ.get(
        "TEST_DATABASE_URL", "sqlite:///./test_db.db"
    )
    # SQLALCHEMY_DATABASE_URL = "postgresql://rosterapi:QPoXzhMFdXhyLeo7stJDsR5PSaDe7Kpmj5nb4Cnf@localhost/rosterapi"
    connect_args = {}
    if "sqlite" in SQLALCHEMY_DATABASE_URL:
        connect_args = {"check_same_thread": False}
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)

    SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionTesting(bind=connection)  # bind=engine)  #
    Base.metadata.create_all(engine)
    yield session
    session.rollback()
    Base.metadata.drop_all(engine)
    session.close()
    transaction.rollback()
    connection.close()


#    os.remove("./test_db.db")


@pytest.fixture(scope="function")
def app_client(db: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    def _create_session():
        try:
            yield db
        finally:
            ...

    app.dependency_overrides[get_session] = _create_session

    with TestClient(app) as client:
        yield client


# @pytest.fixture()
# def create_organisation(db: Session) -> Generator[Organisation, None, None]:
#     organisation = Organisation(name="Test Organisation", tz="Australia/Brisbane")
#     db.add(organisation)
#     db.flush()
#     yield organisation
#     db.rollback()


# @pytest.fixture()
# def create_roster(
#     db: Session, create_organisation: Organisation
# ) -> Generator[Roster, None, None]:
#     roster = Roster(
#         start=date(2023, 1, 1),
#         end=date(2023, 1, 14),
#         name="PP1",
#         organisation=create_organisation,
#     )
#     db.add(roster)
#     db.flush()
#     yield roster
#     db.rollback()


# @pytest.fixture()
# def create_worker(
#     db: Session, create_organisation: Organisation
# ) -> Generator[Worker, None, None]:
#     worker = Worker(
#         surname="McTesterson",
#         given_name="Testy",
#         pref_name="Test",
#         organisation=create_organisation,
#     )
#     db.add(worker)
#     db.flush()
#     yield worker
#     db.rollback()


# @pytest.fixture()
# def create_shift(db: Session, create_roster: Roster) -> Generator[Shift, None, None]:
#     shift = Shift(
#         start=datetime(2023, 1, 3, 8, 0),
#         end=datetime(2023, 1, 3, 20, 30),
#         roster=create_roster,
#         min_requirement=1,
#         max_requirement=2,
#         hours=12,
#     )
#     db.add(shift)
#     db.flush()
#     yield shift
#     db.rollback()


# @pytest.fixture
# def create_tag(
#     db: Session, create_organisation: Organisation
# ) -> Generator[Tag, None, None]:
#     tag = Tag(label="Test", organisation_id=create_organisation.id)
#     db.add(tag)
#     db.flush()
#     yield tag
#     db.rollback()