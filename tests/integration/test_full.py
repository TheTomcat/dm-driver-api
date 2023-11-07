from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from PIL import Image as PImage

from api.models import Combat, Participant
from api.schemas import ParticipantCreate
from api.services import ParticipantService

def test_integration(db: Session, create_images: list[str]):
    pass
    # assert create_all['images'][0].id != create_all['images'][1].id
    # with PImage.open(create_all['images'][0].path) as f:
    #     f.show()

