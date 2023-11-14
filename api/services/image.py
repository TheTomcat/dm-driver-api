from io import BytesIO

from fastapi import HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from PIL import Image as PImage
from sqlalchemy import delete, func, insert, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from api.models import Image, Tag, image_tags
from api.schemas import ImageB64, ImageCreate, ImageMatchResult, ImageScale, ImageUpdate
from api.utils.image_helper import calculate_thumbnail_size, get_image_as_base64

from .base import BaseService


class ImageService(BaseService[Image, ImageCreate, ImageUpdate]):
    def __init__(self, db_session: Session):
        super(ImageService, self).__init__(Image, db_session)

    def get_random(self, *conditions) -> Image:
        return self.db_session.scalar(select(Image).where(*conditions).order_by(func.random()))

    def apply_tag(self, image_id, tag_id) -> Image:
        try:
            q = insert(image_tags).values(image_id=image_id, tag_id=tag_id)
            self.db_session.execute(q)
        except DBAPIError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database error - perhaps the image is already tagged",
            )

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong"
            )
        self.db_session.commit()
        return self.get(image_id)
        # image = self.get(image_id)
        # tag = self.db_session.scalar(select(Tag).where(Tag.id == tag_id))
        # if not tag:
        #     raise HTTPException(status_code=404, detail=f"<Tag id={tag_id}> not found.")
        # image.tags.append(tag)
        # self.db_session.commit()
        # return image

    def remove_tag(self, image_id, tag_id) -> Image:
        try:
            q = delete(image_tags).where(
                image_tags.c.image_id == image_id, image_tags.c.tag_id == tag_id
            )
            self.db_session.execute(q)
        except DBAPIError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database error - perhaps the image is already tagged",
            )

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong."
            )
        self.db_session.commit()
        return self.get(image_id)
        # image = self.get(image_id)
        # tag = self.db_session.scalar(select(Tag).where(Tag.id == tag_id))
        # if not tag:
        #     raise HTTPException(status_code=404, detail=f"<Tag id={tag_id}> not found.")
        # try:
        #     image.tags.remove(tag)
        # except ValueError:
        #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        # self.db_session.commit()
        # return image

    def set_tags(self, image_id, tags: list[int]) -> Image:
        image = self.get(image_id)
        if not image:
            raise HTTPException(status_code=404, detail=f"<Image id={image_id}> not found.")
        tag_objs = self.db_session.scalars(select(Tag).where(Tag.id.in_(tags))).all()
        image.tags = [*tag_objs]
        self.db_session.commit()
        return image

    def get_images_by_tag_match(self, taglist: list[int], transformer=None) -> ImageMatchResult:  # type: ignore
        if transformer is None:

            def transformer(x):
                return x

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
        return ImageMatchResult(
            **{
                "matches": [
                    {
                        "image": transformer(res[0]),
                        "image_id": res[1],
                        "match_count": res[2],
                        "tags": res[3].split(","),
                    }
                    for res in results
                ],
                "tags": taglist,
            }
        )

    def get_full_image(self, image_id: int) -> FileResponse:
        image = self.get(image_id)
        try:
            # with open(image.path) as image_data:
            return FileResponse(image.path, media_type="image/png")
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"<Image id={image_id}> path not found.")
        except Exception:
            raise HTTPException(status_code=500, detail="Server-side error.")

    def get_thumbnail(self, image_id: int, scale: ImageScale) -> StreamingResponse:
        image = self.get(image_id)
        dimensions = calculate_thumbnail_size(
            (image.dimension_x, image.dimension_y), **scale.model_dump()
        )
        try:
            with PImage.open(image.path) as p_image:
                p_image.thumbnail(dimensions)
                image_io = BytesIO()
                p_image.save(image_io, "png")
                image_io.seek(0)
                return StreamingResponse(image_io, media_type="image/png")
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"<Image id={image_id}> path not found.")
        except Exception:
            raise HTTPException(status_code=500, detail="Server-side error.")

    def get_as_base64(self, image_id: int) -> ImageB64:
        image = self.get(image_id)
        try:
            setattr(image, "b64", get_image_as_base64(image.path))
            output = ImageB64.model_validate(image)
            return output
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found on the server."
            )
        except OSError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occured. Perhaps the image path is invalid. {image.path}",
            )
