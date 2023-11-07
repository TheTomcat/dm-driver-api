import enum
from os import PathLike
from typing import Optional

import httpx
from core.view import view
from core.db import CSV, Base

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

class ImageType(enum.Enum):
    backdrop = 'backdrop'
    character = 'character'
    handout = 'handout'
    map = 'map'

def hash_fn(f):
    e = '1253467890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
    return ''.join(random.choices(e,k=20))

class Image(Base):
    #__tablename__ = "images"
    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String(256), index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    focus_x: Mapped[int] = mapped_column(nullable=True, default=-1)
    focus_y: Mapped[int] = mapped_column(nullable=True, default=-1)
    hash: Mapped[str] = mapped_column(String(20), index=True)
    dimension_x: Mapped[int]
    dimension_y: Mapped[int]
    tags: Mapped[list["Tag"]] = relationship(
        back_populates="images", secondary=image_tags
    )
    type: Mapped[ImageType] = mapped_column(default=ImageType.backdrop)

    @classmethod
    def create_from_local_file(cls, path: PathLike, **kwargs) -> 'Image':
        with PImage.open(path) as f:
            (x,y) = f.size
            imhash = hash_fn(f)
        i = cls(path=str(path), name=path.stem, **kwargs, dimension_x=x, dimension_y=y, hash=imhash)
        return i
    
    @classmethod
    def create_from_uri(cls, uri: str, **kwargs) -> 'Image':
        response = httpx.get(uri)
        with PImage.open(response) as f:
            (x,y) = f.size
            imhash = hash_fn(f)
        i = cls(path=uri, **kwargs, dimension_x=x, dimension_y=y, hash=imhash)
        return i
    

class Tag(Base):
    #__tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    tag: Mapped[str] = mapped_column(String(30))
    images: Mapped[list["Image"]] = relationship(
        back_populates="tags", secondary=image_tags
    )

    def __init__(self, tag: str):
        self.tag = tag.lower()
        super(Tag).__init__()


class Message(Base):
    #__tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str] = mapped_column(String(400))

    @classmethod
    def get_random(cls):
        return select(cls).order_by(func.random())

class Session(Base):
    #__tablename__ = "sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), insert_default="")
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id"))
    image: Mapped["Image"] = relationship("Image")
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"))
    message: Mapped["Message"] = relationship("Message")


class Combat(Base):
    __tablename__ = "combat"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), insert_default="")
    participants: Mapped[list["Participant"]] = relationship(back_populates="combat")

class Participant(Base):
    #__tablename__ = "participants"
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

class Entity(Base):
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
