from colorthief import ColorThief


def extract_pallete(image_path, depth=5, quality=2):
    c = ColorThief(image_path)
    return c.get_palette(color_count=depth, quality=quality)


# import timeit

# timeit.timeit('extract_pallete("D:\\RPGs\\Backdrops\\Abandonned Boat (1).png", quality=1)')
