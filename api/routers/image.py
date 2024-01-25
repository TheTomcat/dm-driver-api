from typing import Any, Optional

from fastapi import Depends, Query, Response, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.routing import APIRouter
from fastapi_pagination import Page
from typing_extensions import Annotated

import api.models as models
from api.schemas import Image, ImageB64, ImageCreate, ImageFilter, ImageScale, ImageUpdate, ImageURL
from api.services import ImageService, get_image_service
from api.utils.filters import generate_filter_query

# from core.colour import put_pallete_into_db
from core.db import foreign_key

router = APIRouter(prefix="/image")


# def build_transformer(router: APIRouter, **context):
#     return lambda x: list(map(partial(inject_urls, router=router, **context), x))  # type: ignore


# def inject_urls(model: models.Image, router: APIRouter, **context):
#     return model.inject_urls(router, **context)
# url = router.url_path_for("get_full_image", image_id=model.id)
# thumbnail_url = router.url_path_for("get_image_thumbnail", image_id=model.id, **context)
# model.url = url  # type: ignore
# model.thumbnail_url = thumbnail_url  # type: ignore
# return model


# def inject_urls(model: Image, url: str, thumbnail_url: str) -> ImageURL:


@router.get("/", response_model=Page[ImageURL], tags=["images"])
async def list_images(
    image_service: Annotated[ImageService, Depends(get_image_service)],
    image_filter: Annotated[ImageFilter, Depends()],
    # current_user: CurrentActiveUser,
) -> Page[models.Image]:
    "Get all images"
    q = generate_filter_query(models.Image, image_filter)
    return image_service.get_some(q)  # , transformer=build_transformer(router))


@router.get("/tag", tags=["images"])
async def get_image_tag_matches(
    taglist: Annotated[list[int], Query()],
    image_filter: Annotated[ImageFilter, Depends()],
    image_service: Annotated[ImageService, Depends(get_image_service)],
) -> Page[ImageURL]:  # ImageMatchResult:
    # def transformer(i):
    # return inject_urls(i, router)

    q = generate_filter_query(models.Image, image_filter)
    return image_service.get_images(q, taglist)  # , transformer=build_transformer(router))
    # return image_service.get_images_by_tag_match(taglist, transformer=transformer)


# @router.get("/search", tags=["images"])
# async def smart_search(
#     q: str,
#     image_service: Annotated[ImageService, Depends(get_image_service)],
# ) -> Page[ImageURL]:
#     return image_service.smart_search(query=q)


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
    return image_service.get_random(models.Image.type == image_type)
    # return inject_urls(image_service.get_random(models.Image.type == image_type), router)


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
    return image_service.get(image_id)
    # return inject_urls(image_service.get(image_id), router)


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


# @router.post("/{image_id}/favourite", response_model=Image, tags=["images"])
# async def favourite_image(
#     self,
#     image_id: foreign_key,
#     image_service: Annotated[ImageService, Depends(get_image_service)],
# ) -> models.Image:
#     return image_service.favourite_image(image_id)


@router.post("/upload", response_model=ImageURL, tags=["images"])
async def upload_image(
    image_file: UploadFile,
    # image: ImageUpload,
    # image_name: str,
    # image_type: models.ImageType,
    image_service: Annotated[ImageService, Depends(get_image_service)],
    # background_tasks: BackgroundTasks,
):
    i = await image_service.upload_image(image_file)  # , image_name, image_type)
    # background_tasks.add_task(put_pallete_into_db, i, image_service.db_session)

    return i
    # raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
    # image = image_service.get(image_id)
    # try:
    #     with open(image.path, "rb") as f:
    #         f.write(imdata.read)  # type: ignore
    # except Exception:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # return Response(status_code=200)
    # # filedata = await imdata.read()


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
    return image_service.get_as_base64(image_id)


@router.patch("/{image_id}/collection", response_model=Image, tags=["images"])
async def add_to_collection(
    image_id: foreign_key,
    collection_id: foreign_key,
    image_service: Annotated[ImageService, Depends(get_image_service)],
    # current_user: CurrentActiveUser,
) -> models.Image:
    return image_service.add_to_collection(image_id, collection_id)


@router.delete("/{image_id}/collection", response_model=Image, tags=["images"])
async def remove_from_collection(
    image_id: foreign_key,
    collection_id: foreign_key,
    image_service: Annotated[ImageService, Depends(get_image_service)],
    # current_user: CurrentActiveUser,
) -> Optional[models.Image]:
    return image_service.remove_from_collection(image_id, collection_id)
