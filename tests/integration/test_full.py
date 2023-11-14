from fastapi.testclient import TestClient  # noqa: F401
from PIL import Image as PImage  # noqa: F401
from sqlalchemy.exc import IntegrityError  # noqa: F401
from sqlalchemy.orm import Session

from api.models import Combat, Participant  # noqa: F401
from api.schemas import ParticipantCreate  # noqa: F401
from api.services import ParticipantService  # noqa: F401


def test_integration(db: Session, create_images: list[str]):
    pass
    # assert create_all['images'][0].id != create_all['images'][1].id
    # with PImage.open(create_all['images'][0].path) as f:
    #     f.show()
