from pydantic import ValidationError
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.models import Image, ImageType, Tag
from api.schemas import ImageCreate, ImageScale
from api.services import ImageService

def test_image_create_db(db: Session) -> None:
    t1 = Image(name="Test.png", path="D:\\A\\Path\\To\\Images\\Test.png", dimension_x=1024, dimension_y=1024, hash="1234", type=ImageType.backdrop)
    t2 = Image(name="Test2.png", path="D:\\A\\Path\\To\\Images\\Test2.png", dimension_x=1024, dimension_y=1024, hash="3342", type=ImageType.backdrop)
    db.add_all([t1, t2])
    db.commit()
    assert t1 != t2

def test_image_create_service(image_service: ImageService) -> None:
    t1 = image_service.create(ImageCreate(**{'name':"Test.png", "path":"D:\\A\\Path\\To\\Images\\Test.png",'dimension_x':1024, 'dimension_y':1024, 'hash':"1234", "type":ImageType.backdrop}))
    assert t1.name == 'Test.png'
    with pytest.raises(ValidationError):
        t1 = image_service.create(ImageCreate(**{"path":"D:\\A\\Path\\To\\Images\\Test.png",'dimension_x':1024, 'dimension_y':1024, 'hash':"1234", "type":ImageType.backdrop}))
    with pytest.raises(ValidationError):
        t1 = image_service.create(ImageCreate(**{'name':"Test.png", 'dimension_x':1024, 'dimension_y':1024, 'hash':"1234", "type":ImageType.backdrop}))
    with pytest.raises(ValidationError):
        t1 = image_service.create(ImageCreate(**{'name':"Test.png", "path":"D:\\A\\Path\\To\\Images\\Test.png", 'dimension_y':1024, 'hash':"1234", "type":ImageType.backdrop}))
    with pytest.raises(ValidationError):
        t1 = image_service.create(ImageCreate(**{'name':"Test.png", "path":"D:\\A\\Path\\To\\Images\\Test.png",'dimension_x':1024, 'hash':"1234", "type":ImageType.backdrop}))

def test_image_create_client(app_client: TestClient) -> None:
    rv = app_client.post(
        "/image", json={'name':"Test.png", "path":"D:\\A\\Path\\To\\Images\\Test.png",'dimension_x':1024, 'dimension_y':1024, 'hash':"1234", "type":"backdrop"}
    )
    assert rv.status_code == 201
    assert rv.json()["image_id"] is not None

def test_image_get_many_client(app_client: TestClient) -> None:
    rv = app_client.get("/image")
    assert rv.status_code == 200

def test_image_delete_client(app_client: TestClient, create_image: Image) -> None:
    rv = app_client.get(f"/image/{create_image.id}")
    assert rv.status_code == 200
    rv = app_client.delete(f"/image/{create_image.id}")
    assert rv.status_code == 204
    rv = app_client.get(f"/image/{create_image.id}")
    assert rv.status_code == 404


def test_image_update_client(app_client: TestClient, create_image: Image) -> None:
    assert create_image.name == create_image.name
    rv = app_client.patch(
        f"/image/{create_image.id}", json={"name": (new_filename := "NewFilename.png")}
    )
    image_json = rv.json()
    assert rv.status_code == 200, image_json
    assert create_image.name == new_filename

def test_image_thumbnail_validation_schema():
    valid_1 = {'width': 300}
    valid_2 = {'height': 300}
    valid_3 = {**valid_1, **valid_2}
    valid_4 = {'scale': 0.25}
    invalid_1 = {**valid_1, **valid_4}

    ImageScale(**valid_1)
    ImageScale(**valid_2)
    ImageScale(**valid_3)
    ImageScale(**valid_4)

    with pytest.raises(Exception):
        ImageScale(**invalid_1)


def test_image_add_remove_tag_client(app_client: TestClient, create_image: Image, create_tag: Tag) -> None:
    rv = app_client.get(f"/image/{create_image.id}")
    assert rv.json()['tags'] == []
    rv = app_client.patch(
        f"/image/{create_image.id}/tag?tag_id={create_tag.id}"
    )
    assert rv.status_code == 200
    assert len(rv.json()['tags']) == 1
    rv = app_client.delete(
        f"/image/{create_image.id}/tag?tag_id={create_tag.id}"
    )
    assert rv.status_code == 200
    assert len(rv.json()['tags']) == 0

def test_image_set_tags_client(app_client: TestClient, create_image: Image, create_tag: Tag) -> None:
    rv = app_client.get(f"/image/{create_image.id}")
    assert rv.json()['tags'] == []
    rv = app_client.put(
        f"/image/{create_image.id}/tag",
        json=[create_tag.id]
    )
    assert rv.status_code == 200
    assert len(rv.json()['tags']) == 1
    

def test_image_fetch_client(app_client: TestClient, create_real_images: list[Image]) -> None:
    big = app_client.get(f"/image/{create_real_images[4].id}/full")
    assert big.status_code == 200
    
    assert big.num_bytes_downloaded > 600
    sml = app_client.get(f"/image/{create_real_images[4].id}/thumb?width=50")
    assert len(big.content) > len(sml.content) 

    b64 = app_client.get(f"/image/{create_real_images[4].id}/b64")
    data = b64.json()
    assert 'b64' in data
    assert len(data['b64']) > 1000
    

def test_image_fetch_thumbnail_client(app_client: TestClient, create_image: Image) -> None:
    pass