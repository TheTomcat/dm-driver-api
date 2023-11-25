from functools import partial
from typing import Any, Optional

from fastapi import Depends, HTTPException, Query, Response, UploadFile, status
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.routing import APIRouter
from fastapi_pagination import Page
from typing_extensions import Annotated

import api.models as models
from api.schemas import (
    Image,
    ImageB64,
    ImageCreate,
    ImageFilter,
    ImageScale,
    ImageUpdate,
    ImageURL,
)
from api.services import ImageService, get_image_service
from api.utils.filters import generate_filter_query
from core.db import foreign_key

router = APIRouter(prefix="/image")


def build_transformer(router: APIRouter, **context):
    return lambda x: list(map(partial(inject_urls, router=router, **context), x))


def inject_urls(model: models.Image, router: APIRouter, **context):
    model = model
    url = router.url_path_for("get_full_image", image_id=model.id)
    thumbnail_url = router.url_path_for("get_image_thumbnail", image_id=model.id, **context)
    model.url = url  # type: ignore
    model.thumbnail_url = thumbnail_url  # type: ignore
    return model


@router.get("/", response_model=Page[ImageURL], tags=["images"])
async def list_images(
    image_service: Annotated[ImageService, Depends(get_image_service)],
    image_filter: Annotated[ImageFilter, Depends()],
    # current_user: CurrentActiveUser,
) -> Page[models.Image]:
    "Get all images"
    q = generate_filter_query(models.Image, image_filter)
    return image_service.get_some(q, transformer=build_transformer(router))


@router.get("/tag", tags=["images"])
async def get_image_tag_matches(
    taglist: Annotated[list[int], Query()],
    image_filter: Annotated[ImageFilter, Depends()],
    image_service: Annotated[ImageService, Depends(get_image_service)],
) -> Page[ImageURL]:  # ImageMatchResult:
    def transformer(i):
        return inject_urls(i, router)

    q = generate_filter_query(models.Image, image_filter)
    return image_service.get_images(q, taglist, transformer=build_transformer(router))
    # return image_service.get_images_by_tag_match(taglist, transformer=transformer)


@router.get(
    "/random",
    response_model=ImageURL,
    responses={404: {"description": "Image not found"}},
    tags=["images"],
)
async def get_random_image(
    image_type: models.ImageType,
    image_service: Annotated[ImageService, Depends(get_image_service)],
    # current_user: CurrentActiveUser,
) -> models.Image:
    "Get a single random image"
    return inject_urls(image_service.get_random(models.Image.type == image_type), router)


@router.get(
    "/{image_id}",
    response_model=ImageURL,
    responses={404: {"description": "Image not found"}},
    tags=["images"],
)
async def get_image(
    image_id: foreign_key,
    image_service: Annotated[ImageService, Depends(get_image_service)],
    # current_user: CurrentActiveUser,
) -> models.Image:
    "Get a single image by id"
    return inject_urls(image_service.get(image_id), router)


@router.post(
    "/",
    response_model=Image,
    status_code=201,
    responses={409: {"description": "Conflict Error"}},
    tags=["images"],
)
async def create_image(
    image: ImageCreate,
    image_service: Annotated[ImageService, Depends(get_image_service)],
    # current_user: CurrentActiveUser,
) -> models.Image:
    "Create a new image"
    return image_service.create(image)


@router.patch("/{image_id}", response_model=Image, tags=["images"])
async def update_image(
    image_id: foreign_key,
    image: ImageUpdate,
    image_service: Annotated[ImageService, Depends(get_image_service)],
    # current_user: CurrentActiveUser,
) -> Optional[models.Image]:
    return image_service.update(image_id, image)


# @router.delete('/{image_id}/data', tags=['images'])
# async def upload_image(
#     image_id: foreign_key,
#     image_service: Annotated[ImageService, Depends(get_image_service)],
# ):
#     image = image_service.get(image_id)
#     return Response(status_code=status.HTTP_200_OK)
#         # filedata = await imdata.read()


@router.patch("/{image_id}/data", tags=["images"])
async def upload_image(
    image_id: foreign_key,
    imdata: UploadFile,
    image_service: Annotated[ImageService, Depends(get_image_service)],
):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
    image = image_service.get(image_id)
    try:
        with open(image.path, "rb") as f:
            f.write(imdata.read)  # type: ignore
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(status_code=200)
    # filedata = await imdata.read()


@router.patch("/{image_id}/tag", response_model=Image, tags=["images"])
async def apply_tag(
    image_id: foreign_key,
    tag_id: foreign_key,
    image_service: Annotated[ImageService, Depends(get_image_service)],
    # current_user: CurrentActiveUser,
) -> models.Image:
    return image_service.apply_tag(image_id, tag_id)


@router.delete("/{image_id}/tag", response_model=Image, tags=["images"])
async def remove_tag(
    image_id: foreign_key,
    tag_id: foreign_key,
    image_service: Annotated[ImageService, Depends(get_image_service)],
    # current_user: CurrentActiveUser,
) -> Optional[models.Image]:
    return image_service.remove_tag(image_id, tag_id)


@router.put("/{image_id}/tag", response_model=Image, tags=["images"])
async def set_tags(
    image_id: foreign_key,
    tags: list[int],
    image_service: Annotated[ImageService, Depends(get_image_service)],
    # current_user: CurrentActiveUser,
) -> Optional[models.Image]:
    return image_service.set_tags(image_id, tags)


@router.delete("/{image_id}", tags=["images"])  # , status_code=204)
async def delete_image(
    image_id: foreign_key,
    image_service: Annotated[ImageService, Depends(get_image_service)],
    # current_user: CurrentActiveUser,
) -> Any:
    image_service.delete(image_id)
    return Response(status_code=204)


@router.get(
    "/{image_id}/full",
    responses={404: {"description": "Image not found"}},
    response_class=FileResponse,
    tags=["images"],
)
async def get_full_image(
    image_id: foreign_key, image_service: Annotated[ImageService, Depends(get_image_service)]
) -> Any:
    return image_service.get_full_image(image_id)


@router.get(
    "/{image_id}/thumb",
    responses={404: {"description": "Image not found"}},
    response_class=StreamingResponse,
    tags=["images"],
)
async def get_image_thumbnail(
    image_id: foreign_key,
    scale: Annotated[ImageScale, Depends()],
    image_service: Annotated[ImageService, Depends(get_image_service)],
    # responses={401: {}}
) -> Any:
    return image_service.get_thumbnail(image_id, scale)


@router.get(
    "/{image_id}/b64",
    responses={404: {"description": "Image not found"}},
    response_model=ImageB64,
    tags=["images"],
)
async def get_image_as_base64(
    image_id: foreign_key,
    image_service: Annotated[ImageService, Depends(get_image_service)],
) -> Any:
    return image_service.get_as_base64(image_id)
