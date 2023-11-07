import base64

def calculate_thumbnail_size(image_dimension, **dimensions):
    match dimensions:
        case {"width": width, "height": height} if width is not None and height is not None:
            scf = min(
                width / image_dimension[0],
                height / image_dimension[1],
            )
        case {"width": width} if width is not None:
            scf = width / image_dimension[0]
        case {"height": height} if height is not None:
            scf = height / image_dimension[1]
        case {"scale": scale} if scale is not None:
            scf = scale
        case _:
            raise IndexError("Dimensions must have either scale, or one or more of width and height")
    return (
        int(scf * image_dimension[0]),
        int(scf * image_dimension[1]),
    )

def get_image_as_base64(path):
    with open(path, "rb") as image:
        data = base64.b64encode(image.read())
    return data.decode("ascii")

