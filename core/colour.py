from colorthief import ColorThief

# from sqlalchemy.orm import Session

# from api.models import Image
# from core.utils import rgb_to_hex


def extract_pallete(image_path, depth=5, quality=2):
    c = ColorThief(image_path)
    return c.get_palette(color_count=depth, quality=quality)


# def put_pallete_into_db(image: Image, session: Session):
#     image.palette = ",".join(map(rgb_to_hex, extract_pallete(image.path)))

#     try:
#         session.add(image)
#         session.commit()
#     except Exception as e:
#         session.rollback()
#         raise e


# import timeit

# timeit.timeit('extract_pallete("D:\\RPGs\\Backdrops\\Abandonned Boat (1).png", quality=1)')
# timeit.timeit('extract_pallete("D:\\RPGs\\Backdrops\\Abandonned Boat (1).png", quality=1)')
# timeit.timeit('extract_pallete("D:\\RPGs\\Backdrops\\Abandonned Boat (1).png", quality=1)')
