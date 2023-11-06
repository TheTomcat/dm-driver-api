from typing import Optional
from core.db import Base

from sqlalchemy import Column, String, Table, ForeignKey, select
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import BLOB
# from flask import url_for
from typing_extensions import Annotated

import base64
import math
import random
from PIL import Image as PImage
from pathlib import Path

image_tags = Table(
    "image_tags",
    Base.metadata,
    Column("image_id", ForeignKey("images.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Selector(object):
    @classmethod
    def get_by_id_or_random(cls, id=None):
        if id is None:
            return cls.get_random()
        return select(cls).where(cls.id == id)

    @classmethod
    def get_random(cls):
        return select(cls).order_by(func.random())

    @classmethod
    def get(cls, id):
        return select(cls).where(cls.id == id)


def get_image_as_base64(path):
    with open(path, "rb") as image:
        data = base64.b64encode(image.read())
    return data.decode("ascii")


def get_image_thumbnail_as_base64(image: "Image", scale):
    """scale can be a single number - in which case, scale the image up or down by that fraction,
    or it can be a (width,height) tuple, in which case the image will be resized to fit within that bounding box
    """
    # if isinstance(scale, (int, float)):
    #     aspect_ratio = scale
    # elif isinstance(scale, (tuple, list)):
    #     if len(scale) != 2:
    #         raise IndexError("Scale must be a number or an iterable of length 2")
    #     aspect_ratio = min(scale[0] / image.dimension_x, scale[1] / image.dimension_y)
    with open(image.path, "rb") as f:
        x, y = calculate_thumbnail_size(
            (image.dimension_x, image.dimension_y), scale=scale
        )
        imdata = PImage.open(f)
        imdata.thumbnail((x, y))
        output = base64.b64encode(imdata.tobytes())
        return output.decode("ascii")


def calculate_thumbnail_size(image_dimension, **dimensions):
    match dimensions:
        case {"width": width, "height": height}:
            scf = min(
                width / image_dimension[0],
                height / image_dimension[1],
            )
        case {"width": width}:
            scf = width / image_dimension[0]
        case {"height": height}:
            scf = height / image_dimension[1]
        case {"scale": scale}:
            scf = scale
        case _:
            raise IndexError("Scale must be a number or an iterable of length 2")
    return (
        int(scf * image_dimension[0]),
        int(scf * image_dimension[1]),
    )


class Image(Base, Selector):
    __tablename__ = "images"
    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(30), index=True, unique=True)
    focus_x: Mapped[int] = mapped_column(nullable=True)
    focus_y: Mapped[int] = mapped_column(nullable=True)
    hash: Mapped[str] = mapped_column(String(20), index=True)
    dimension_x: Mapped[int]
    dimension_y: Mapped[int]
    tags: Mapped[list["Tag"]] = relationship(
        back_populates="images", secondary=image_tags
    )
    directory_id: Mapped[int] = mapped_column(ForeignKey("directories.id"))
    directory: Mapped["Directory"] = relationship(back_populates="images")
    # attribution: Mapped[str] = mapped_column(String(300), nullable=True)

    def get_fullsize_image_data_base64(self, base_path=None):
        if base_path is not None:
            raise DeprecationWarning("BasePath should not be used")
        return get_image_as_base64(Path(self.directory.path, self.filename))

    def get_thumbnail_image_data_base64(self, base_path=None):
        if base_path is not None:
            raise DeprecationWarning("BasePath should not be used")
        # return get_image_as_base64(base_path + "thumbnails\\" + self.filename)
        return get_image_thumbnail_as_base64(self, (300, 300))

    @property
    def path(self):
        return Path(self.directory.path, self.filename)

    # @property
    # def url(self):
    #     return url_for("api.get_fullsize_image", image_id=self.id)

    # @property
    # def url_thumbnail(self):
    #     return url_for("api.get_thumbnail_image", image_id=self.id)

    def to_json(self):
        return {
            "image_id": self.id,
            "filename": self.filename,
            "dimensions": (self.dimension_x, self.dimension_y),
            "url": self.url,
            "thumbnail": self.url_thumbnail,
        }


class Directory(Base):
    __tablename__ = "directories"
    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String(256), index=True, unique=True)
    images: Mapped[list["Image"]] = relationship(back_populates="directory")


class Tag(Base, Selector):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    tag: Mapped[str] = mapped_column(String(30))
    images: Mapped[list["Image"]] = relationship(
        back_populates="tags", secondary=image_tags
    )

    def to_json(self):
        return {"tag_id": self.id, "tag": self.tag}


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str] = mapped_column(String(400))

    @classmethod
    def get_random(cls):
        return select(cls).order_by(func.random())

    def to_json(self):
        return {"message_id": self.id, "message": self.message}


class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), insert_default="")
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id"))
    image: Mapped["Image"] = relationship("Image")
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"))
    message: Mapped["Message"] = relationship("Message")

    def to_json(self):
        return {
            "session_id": self.id,
            "title": self.title,
            "message_id": self.message_id,
            "image_id": self.image_id,
        }


class Combat(Base, Selector):
    __tablename__ = "combat"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), insert_default="")
    participants: Mapped[list["Participant"]] = relationship(back_populates="combat")

    def to_json(self):
        return {
            "combat_id": self.id,
            "title": self.title,
            "participants": [
                participant.to_json() for participant in self.participants
            ],
            #             "participants": {
            #     participant.id: participant.to_json()
            #     for participant in self.participants
            # },
        }


class Participant(Base, Selector):
    __tablename__ = "participants"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), insert_default="")
    combat_id: Mapped[int] = mapped_column(ForeignKey("combat.id"))
    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id"), nullable=True)
    combat: Mapped["Combat"] = relationship(back_populates="participants")

    entity: Mapped["Entity"] = relationship()

    is_visible: Mapped[bool] = mapped_column(default=True)
    is_PC: Mapped[bool] = mapped_column(default=False)
    damage: Mapped[int] = mapped_column(default=0)
    max_hp: Mapped[int] = mapped_column(default=0)
    ac: Mapped[int] = mapped_column(default=0)
    initiative: Mapped[int] = mapped_column(default=10)
    initiative_modifier: Mapped[int] = mapped_column(default=0, nullable=True)
    conditions: Mapped[str] = mapped_column(String(256), default="")
    has_reaction: Mapped[bool] = mapped_column(default=True)

    colour: Mapped[str] = mapped_column(String(10), nullable=True)
    image_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("images.id"), nullable=True
    )
    image: Mapped[Optional[Image]] = relationship("Image")

    def to_json(self):
        return {
            "participant_id": self.id,
            "combat_id": self.combat_id,
            "entity_id": self.entity_id,
            "name": self.name,
            "is_visible": self.is_visible,
            "damage": self.damage,
            "max_hp": self.max_hp,
            "ac": self.ac,
            "initiative": self.initiative,
            "initiative_modifier": self.initiative_modifier,
            "conditions": self.conditions.split(","),
            "has_reaction": self.has_reaction,
            "colour": self.colour,
            "image_id": self.image_id,
        }


class Entity(Base, Selector):
    __tablename__ = "entities"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), insert_default="")
    hit_dice: Mapped[str] = mapped_column(String(50), insert_default="")
    ac: Mapped[int] = mapped_column(default=10)
    cr: Mapped[str] = mapped_column(String(10), default="")
    initiative_modifier: Mapped[int] = mapped_column(default=0)
    data: Mapped[str] = mapped_column(BLOB, nullable=True)
    is_PC: Mapped[bool] = mapped_column(default=False)
    image_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("images.id"), nullable=True
    )
    image: Mapped[Optional[Image]] = relationship("Image")
    source: Mapped[str] = mapped_column(String(10), nullable=True)
    source_page: Mapped[int] = mapped_column(nullable=True)

    def to_json(self):
        return {
            "entity_id": self.id,
            "name": self.name,
            "hit_dice": self.hit_dice,
            "ac": self.ac,
            "cr": self.cr,
            "initiative_modifier": self.initiative_modifier,
            "is_PC": self.is_PC,
            "image_id": self.image_id,
            "source": self.source,
            "source_page": self.source_page,
            "data": self.data,
        }


class Focus:
    def __init__(self, image: Image, focus=None):
        self.image = image
        self.dx = image.dimension_x
        self.dy = image.dimension_y
        if focus:
            self.fx = focus[0]
            self.fy = focus[1]
        elif self.image.focus_x is not None:
            self.fx = self.image.focus_x
            self.fy = self.image.focus_y
        else:
            self.fx = -400 + self.dx / 2
            self.fy = self.dy / 2 - 400

    @property
    def params(self):
        return self.fx, self.fy, self.dx, self.dy

    @staticmethod
    def get_zoom(fx, fy, dx, dy):
        return 1 / (2 * min([fx / dx, fy / dy, (dx - fx) / dx, (dy - fy) / dy]))

    @property
    def zoom(self):
        return self.get_zoom(*self.params)  # self.fx, self.fy, self.dx, self.dy)

    @property
    def x(self):
        return self.fx - self.dx / 2

    @property
    def y(self):
        return self.dy / 2 - self.fy

    def wangle(self, angle) -> "Focus":
        r = min(self.image.dimension_x, self.image.dimension_y) / 4
        x = self.image.dimension_x / 2 + r * math.cos(angle) * random.random()
        y = self.image.dimension_y / 2 - r * math.sin(angle) * random.random()
        f = Focus(self.image)
        f.fx = x
        f.fy = y
        return (
            f  # x, y, self.get_zoom(x,y,self.image.dimension_x, self.image.dimension_y)
        )

    @property
    def csstransform(self) -> str:
        return (
            "@keyframes slowpan {"
            "0% {"
            f"   transform:translate3d({self.x}px,{self.y}px,0) scale({self.zoom});"
            "}"
            "50% {"
            f"   transform:translate3d(0,0,0) scale(1.1);"
            "}"
            "100% {"
            f"   transform:translate3d(400px,-200px,0) scale(1.5);"
            "}"
            "}"
        )
