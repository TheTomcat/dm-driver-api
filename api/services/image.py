from io import BytesIO
from fastapi.responses import FileResponse, StreamingResponse

from api.utils.image_helper import calculate_thumbnail_size, get_image_as_base64
from .base import BaseService, ModelType
from sqlalchemy.orm import Session
from sqlalchemy import select, func, text
from api.models import Image, Tag, image_tags
from api.schemas import ImageB64, ImageCreate, ImageMatchResult, ImageScale, ImageUpdate
from typing import Optional
from fastapi import HTTPException, Response, status
from PIL import Image as PImage

class ImageService(
    BaseService[Image, ImageCreate, ImageUpdate]
):
    def __init__(self, db_session: Session):
        super(ImageService, self).__init__(Image, db_session)

    def get_random(self, *conditions):
        return self.db_session.scalar(select(Image).where(*conditions).order_by(func.random()))

    def apply_tag(self, image_id, tag_id) -> Optional[Image]:
        image = self.get(image_id)
        if not image:
            return Response(status_code=404)
        tag = self.db_session.scalar(select(Tag).where(Tag.id==tag_id))
        image.tags.append(tag)
        self.db_session.commit()
        return image

    def remove_tag(self, image_id, tag_id) -> Optional[Image] | Response:
        image = self.get(image_id)
        tag = self.db_session.scalar(select(Tag).where(Tag.id==tag_id))
        try:
            image.tags.remove(tag)
        except ValueError as e:
            return Response(status_code=404)
        self.db_session.commit()
        return image
    
    def set_tags(self, image_id, tags: list[str]) -> Optional[Image]:
        image = self.get(image_id)
        if not image:
            return Response(status_code=404)
        tag_objs = self.db_session.scalars(select(Tag).where(Tag.id.in_(tags))).all()
        image.tags = tag_objs
        self.db_session.commit()
        return image

    def get_images_by_tag_match(self, taglist: list[int]) -> ImageMatchResult:
        q = (
        select(
            Image,
            image_tags.c.image_id.label("match_id"),
            func.count(image_tags.c.image_id).label("match_count"),
            func.aggregate_strings(image_tags.c.tag_id, ",").label("tags"),
        )
        .join(Image, Image.id == image_tags.c.image_id)
        .where(image_tags.c.tag_id.in_(taglist))
        .group_by(image_tags.c.image_id)
        .order_by(text("match_count DESC"))
        .limit(12)
    )
        results = self.db_session.execute(q).all()
        return {'matches': [{
                    'image':res[0], 
                    'image_id':res[1], 
                    'match_count':res[2], 
                    'tags':res[3].split(',')
                        } for res in results],
                'tags':taglist
            }
    
    def get_full_image(self, image_id: int) -> FileResponse:
        image = self.get(image_id)
        if not image:
            return Response(status_code=404)
        try:
            #with open(image.path) as image_data:
            return FileResponse(image.path, media_type="image/png")
        except FileNotFoundError:
            return Response(status_code=404)
        except Exception as e:
            return Response(status_code=500)
        
    def get_thumbnail(self, image_id: int, scale: ImageScale) -> StreamingResponse:
        image = self.get(image_id)
        dimensions = calculate_thumbnail_size((image.dimension_x, image.dimension_y), **scale.model_dump())
        if not image:
            return Response(status_code=404)
        try:
            with PImage.open(image.path) as p_image:
                p_image.thumbnail(dimensions)
                image_io = BytesIO()
                p_image.save(image_io, 'png')
                image_io.seek(0)
                return StreamingResponse(image_io, media_type='image/png')
        except FileNotFoundError:
            return Response(status_code=404)
        except Exception as e:
            return Response(status_code=500)
        
    def get_as_base64(self, image_id: int) -> ImageB64:
        image = self.get(image_id)
        if not image:
            return Response(status_code=404)
        try:
            image.b64 = get_image_as_base64(image.path)
            return image
        except Exception as e:
            return Response(500)
        

