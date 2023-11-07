from collections import defaultdict
import os
from datetime import date, datetime
from pathlib import Path
import random
from typing import Generator

import pytest
from PIL import Image as PImage, ImageDraw
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as DBSession, sessionmaker

from api.api import create_app
from api.models import Combat, Entity, Image, ImageType, Message, Participant, Tag, Session
# from api.db.models import Base, Organisation, Roster, Shift, Tag, Worker
from core.session import get_session
from core.db import Base
from api.services import (
    TagService, 
    ImageService, 
    SessionService,
    MessageService, 
    CombatService, 
    ParticipantService, 
    EntityService, 
    get_image_service, 
    get_message_service, 
    get_session_service, 
    get_tag_service, 
    get_combat_service, 
    get_entity_service, 
    get_participant_service
)


@pytest.fixture(scope="session")
def db() -> Generator[DBSession, None, None]:
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


    # os.remove("./test_db.db")


@pytest.fixture(scope="function")
def app_client(db: DBSession) -> Generator[TestClient, None, None]:
    app = create_app()

    def _create_session():
        try:
            yield db
        finally:
            ...

    app.dependency_overrides[get_session] = _create_session

    with TestClient(app) as client:
        yield client


@pytest.fixture()
def tag_service(db: DBSession) -> TagService:
    return get_tag_service(db)

@pytest.fixture()
def image_service(db: DBSession) -> ImageService:
    return get_image_service(db)

@pytest.fixture()
def message_service(db: DBSession) -> MessageService:
    return get_message_service(db)

@pytest.fixture()
def session_service(db: DBSession) -> SessionService:
    return get_session_service(db)

@pytest.fixture()
def combat_service(db: DBSession) -> CombatService:
    return get_combat_service(db)

@pytest.fixture()
def entity_service(db: DBSession) -> EntityService:
    return get_entity_service(db)

@pytest.fixture()
def participant_service(db: DBSession) -> ParticipantService:
    return get_participant_service(db)

@pytest.fixture()
def create_tag(db: DBSession) -> Generator[Tag, None, None]:
    tag = Tag(tag="test")
    db.add(tag)
    db.flush()
    yield tag
    db.rollback()

@pytest.fixture()
def create_image(db: DBSession) -> Generator[Image, None, None]:
    image = Image(name="Test.png", path="D:\\A\\Path\\To\\The\\Images\\Test.png", dimension_x=1024, dimension_y=1024, hash="1234", type=ImageType.backdrop)
    db.add(image)
    db.flush()
    yield image
    db.rollback()

@pytest.fixture()
def create_message(db: DBSession) -> Generator[Message, None, None]:
    message = Message(message="A test message")
    db.add(message)
    db.flush()
    yield message
    db.rollback()

@pytest.fixture()
def create_session(db: DBSession, create_image: Image, create_message: Message) -> Generator[Session, None, None]:
    session = Session(image_id = create_image.id, message_id=create_message.id)
    db.add(session)
    db.flush()
    yield session
    db.rollback()

@pytest.fixture()
def create_combat(db: DBSession) -> Generator[Combat, None, None]:
    combat = Combat(title="A new and glorious combat")
    db.add(combat)
    db.flush()
    yield combat
    db.rollback()

@pytest.fixture()
def create_entity(db: DBSession) -> Generator[Entity, None, None]:
    entity = Entity("TODO!!!!")
    db.add(entity)
    db.flush()
    yield entity
    db.rollback()

@pytest.fixture()
def create_participant(db: DBSession, create_combat: Combat) -> Generator[Participant, None, None]:
    participant =Participant(name="Test Participant 1", is_visible=True, is_PC = False, combat_id=create_combat.id,
                     damage=10, max_hp=20, ac=11, initiative=12, initiative_modifier=5, 
                     conditions='surprised', has_reaction=True, colour="#0ff00f")
    db.add(participant)
    db.flush()
    yield participant
    db.rollback()

@pytest.fixture()
def create_image_files(db: DBSession, tmp_path: Path):
    # Create 3 blank backdrops and 5 character images, and a handout and map for good measure
    types = [ImageType.backdrop]*3 + [ImageType.backdrop]*5 + [ImageType.handout] + [ImageType.map]
    filenames = [f'{i+1}.png' for i in range(10)]
    images = []
    for filename, type in zip(filenames, types):
        width, height = 2912, 1632
        image = PImage.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)
        for _ in range(50):
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            x2 = random.randint(x, width-1)
            y2 = random.randint(y, height-1)
            col =  (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            draw.rectangle((x,y,x2,y2), fill=col)
        image.save(path:=tmp_path.joinpath(filename))
        images.append(path)
    return images
    
@pytest.fixture()
def create_real_images(db: DBSession, create_image_files: list[Path]):
    # Create 3 blank backdrops and 5 character images, and a handout and map for good measure
    random_type = lambda : random.choice(list(ImageType.__members__))
    images = []
    for path in create_image_files:
        i = Image.create_from_local_file(path, type=random_type())
        images.append(i)
        db.add(i)
    db.flush()
    yield images