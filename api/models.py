import enum
import math
import pathlib
import random
from typing import Optional

import httpx
from fastapi import HTTPException
from PIL import Image as PImage
from PIL import UnidentifiedImageError
from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import BLOB

from core.colour import extract_pallete
from core.db import Base
from core.utils import rgb_to_hex, roll

image_tags = Table(
    "image_tags",
    Base.metadata,
    Column("image_id", ForeignKey("images.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

image_entities = Table(
    "image_entities",
    Base.metadata,
    Column("image_id", ForeignKey("images.id"), primary_key=True),
    Column("entity_id", ForeignKey("entities.id"), primary_key=True),
)

# image_favourites = Table(
#     "image_favourites", Base.metadata, Column("image_id", ForeignKey("images.id"), primary_key=True)
# )

image_collections = Table(
    "image_collections",
    Base.metadata,
    Column("image_id", ForeignKey("images.id"), primary_key=True),
    Column("collection_id", ForeignKey("collections.id"), primary_key=True),
)


class ImageType(enum.Enum):
    backdrop = "backdrop"
    character = "character"
    handout = "handout"
    map = "map"


class ImageOrigin(enum.Enum):
    cli = "cli"
    url = "url"
    upload = "upload"


class SessionMode(enum.Enum):
    loading = "loading"
    backdrop = "backdrop"
    combat = "combat"
    handout = "handout"
    map = "map"
    empty = "empty"


def hash_fn(f):
    e = "1253467890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
    return "".join(random.choices(e, k=20))


class Image(Base):
    # __tablename__ = "images"
    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String(256), index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    focus_x: Mapped[int] = mapped_column(nullable=True, default=-1)
    focus_y: Mapped[int] = mapped_column(nullable=True, default=-1)
    hash: Mapped[str] = mapped_column(String(20), index=True)
    dimension_x: Mapped[int]
    dimension_y: Mapped[int]
    tags: Mapped[list["Tag"]] = relationship(back_populates="images", secondary=image_tags)
    type: Mapped[ImageType] = mapped_column(default=ImageType.backdrop)
    palette: Mapped[str] = mapped_column(String(50), nullable=True)

    collections: Mapped[list["Collection"]] = relationship(
        back_populates="images", secondary=image_collections
    )

    entities: Mapped[list["Entity"]] = relationship(back_populates="image")
    # entities: Mapped['Entity'] = relationship(back_populates="images", secondary=image_entities)

    # origin: Mapped[ImageOrigin] = mapped_column(default=ImageOrigin.cli)
    # attribution: Mapped[str] = mapped_column(String(50))

    @classmethod
    def create_from_local_file(
        cls, path: pathlib.Path, calculate_palette=False, **kwargs
    ) -> "Image":
        with PImage.open(path) as f:
            (x, y) = f.size
            imhash = hash_fn(f)
        name = kwargs.pop("name", path.name).split(".")[0]
        i = cls(
            path=str(path),
            name=name,
            **kwargs,
            dimension_x=x,
            dimension_y=y,
            hash=imhash,
        )
        if calculate_palette:
            i.palette = ",".join(map(rgb_to_hex, extract_pallete(path)))
        return i

    @classmethod
    def create_from_uri(cls, uri: str, **kwargs) -> "Image":
        response = httpx.get(uri)
        try:
            with PImage.open(response) as f:  # type: ignore
                (x, y) = f.size
                imhash = hash_fn(f)
            i = cls(
                path=uri, **kwargs, dimension_x=x, dimension_y=y, hash=imhash
            )  # , origin=ImageOrigin.url)
            return i
        except UnidentifiedImageError:
            raise HTTPException(status_code=404, detail=f"Image at {uri} not found")

    # def inject_urls(self, router: APIRouter, **context):
    #     self.url = router.url_path_for("get_full_image", image_id=self.id)
    #     self.thumbnail_url = router.url_path_for("get_image_thumbnail", image_id=self.id, **context)
    #     return self

    @property
    def url(self):
        return f"/image/{self.id}/full"

    @property
    def thumbnail_url(self):
        return f"/image/{self.id}/thumb"


# class Attribution(Base):
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(50))
#     url: Mapped[str] = mapped_column(String(256))
#     images: Mapped[list["Image"]] = relationship(back_populates="attribution")


class Tag(Base):
    # __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    tag: Mapped[str] = mapped_column(String(30), unique=True)
    images: Mapped[list["Image"]] = relationship(back_populates="tags", secondary=image_tags)

    def __init__(self, tag: str):
        self.tag = tag.lower()
        super(Tag).__init__()


class Message(Base):
    # __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str] = mapped_column(String(400))


class Session(Base):
    # __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    backdrop_id: Mapped[int] = mapped_column(ForeignKey("images.id"), nullable=True)
    backdrop: Mapped["Image"] = relationship("Image", foreign_keys=[backdrop_id])
    overlay_image_id: Mapped[int] = mapped_column(ForeignKey("images.id"), nullable=True)
    overlay_image: Mapped["Image"] = relationship("Image", foreign_keys=[overlay_image_id])
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"), nullable=True)
    message: Mapped["Message"] = relationship("Message")
    combat_id: Mapped[int] = mapped_column(ForeignKey("combat.id"), nullable=True)
    combat: Mapped["Combat"] = relationship("Combat")

    mode: Mapped[str] = mapped_column(String(8), default="empty")  # SessionMode.empty)


class Combat(Base):
    __tablename__ = "combat"  # type: ignore
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), insert_default="")
    round: Mapped[int] = mapped_column(default=0)
    # active_participant_id: Mapped[Optional[int]] = mapped_column(ForeignKey("participants.id"))
    # active_participant: Mapped[Optional["Participant"]] = relationship(
    #     foreign_keys=[active_participant_id]
    # )
    active_participant_id: Mapped[Optional[int]]
    is_active: Mapped[bool] = mapped_column(insert_default=False)
    participants: Mapped[list["Participant"]] = relationship(
        back_populates="combat", primaryjoin="Participant.combat_id==Combat.id"
    )
    # image_id: Mapped[Optional[int]] = mapped_column(ForeignKey("images.id"), nullable=True)
    # image: Mapped[Optional["Image"]] = relationship("Image")


class Participant(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), insert_default="")
    combat_id: Mapped[int] = mapped_column(ForeignKey("combat.id"))
    entity_id: Mapped[Optional[int]] = mapped_column(ForeignKey("entities.id"), nullable=True)
    combat: Mapped["Combat"] = relationship(back_populates="participants")

    entity: Mapped["Entity"] = relationship()

    is_visible: Mapped[bool] = mapped_column(default=True)
    is_PC: Mapped[bool] = mapped_column(default=False)
    damage: Mapped[int] = mapped_column(default=0)
    max_hp: Mapped[int] = mapped_column(default=0)
    hit_dice: Mapped[str] = mapped_column(String(50), default="")
    ac: Mapped[int] = mapped_column(default=0)
    initiative: Mapped[int] = mapped_column(default=None, nullable=True)
    initiative_modifier: Mapped[int] = mapped_column(default=0)
    conditions: Mapped[str] = mapped_column(String(256), default="")
    has_reaction: Mapped[bool] = mapped_column(default=True)

    colour: Mapped[str] = mapped_column(String(10), nullable=True)
    image_id: Mapped[Optional[int]] = mapped_column(ForeignKey("images.id"), nullable=True)
    image: Mapped[Optional[Image]] = relationship("Image")

    @classmethod
    def from_entity(cls, e: "Entity", **kwargs) -> "Participant":
        p = Participant(
            name=kwargs.get("name", e.name),
            entity=e,
            is_visible=kwargs.get("is_visible", True),
            is_PC=kwargs.get("is_PC", e.is_PC),
            damage=0,
            max_hp=kwargs.get("hit_dice", roll(e.hit_dice)),
            hit_dice=kwargs.get("hit_dice", ""),
            ac=kwargs.get("ac", e.ac),
            initiative_modifier=kwargs.get("initiative_modifier", e.initiative_modifier),
            image=e.image,
        )
        return p


class Entity(Base):
    __tablename__ = "entities"  # type: ignore
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), insert_default="")
    is_PC: Mapped[bool] = mapped_column(default=False)

    image_id: Mapped[Optional[int]] = mapped_column(ForeignKey("images.id"), nullable=True)
    image: Mapped[Optional[Image]] = relationship("Image")

    cr: Mapped[float] = mapped_column(nullable=True)
    hit_dice: Mapped[str] = mapped_column(String(50), insert_default="")
    ac: Mapped[int] = mapped_column(default=10)
    initiative_modifier: Mapped[int] = mapped_column(default=0)

    data: Mapped[bytes] = mapped_column(BLOB, nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    source_page: Mapped[Optional[int]] = mapped_column(nullable=True)


class Collection(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    images: Mapped[list["Image"]] = relationship(
        back_populates="collections", secondary=image_collections
    )


# class Favourite(Base):
#     pass

# class EntityData(Base):
#     __tablename__ = "entitydata"  # type: ignore
#     id: Mapped[int] = mapped_column(primary_key=True)
#     entity_id: Mapped[Optional[int]] = mapped_column(ForeignKey("entities.id"))
#     entity: Mapped[Optional["Entity"]] = relationship()

#     STR: Mapped[int] = mapped_column(default=10)
#     DEX: Mapped[int] = mapped_column(default=10)
#     CON: Mapped[int] = mapped_column(default=10)
#     INT: Mapped[int] = mapped_column(default=10)
#     WIS: Mapped[int] = mapped_column(default=10)
#     CHA: Mapped[int] = mapped_column(default=10)

#     saves: Mapped[str] = mapped_column(String(75), insert_default="") ## "str":"+15", 11*6+5
#     skills: Mapped[str] = mapped_column(String(500), insert_default="")
#     senses: Mapped[str] = mapped_column(String(200), insert_default="")
#     speed: Mapped[str] = mapped_column(String(200), insert_default="")

#     damage_vulnerabilities
#     damage_resisrances
#     damage_immunities
#     condition_immunities
#     languages
#     traits
#     actions
#     bonus_actions
#     reactions
#     legendary_actions
#     mythic_actions

# class SpellSchool(enum.Enum):
#     Abjuration = "A"
#     Conjuration = "C"
#     Divination = "D"
#     Enchantment = "E"
#     Evocation = "V"
#     Illusion = "I"
#     Necromancy = "N"
#     Transmutation = "T"


# class SpellDurationType(enum.Enum):
#     timed = "timed"
#     special = "special"
#     instant = "instant"
#     permanent = "permanent"


# class Spell(Base):
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(50), nullable=False)
#     level: Mapped[int]
#     school: Mapped[SpellSchool]
#     source: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
#     source_page: Mapped[Optional[int]] = mapped_column(nullable=True)
#     time_num: Mapped[int]
#     time_unit: Mapped[str] = mapped_column()
#     range: Mapped[str]
#     duration_type: Mapped[SpellDurationType]
#     duration_num: Mapped[int]
#     duration_unit: Mapped[str]
#     has_verbal: Mapped[bool]
#     has_somatic: Mapped[bool]
#     has_material: Mapped[bool]
#     material_component: Mapped[str] = mapped_column(String(50), nullable=True)


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
        return f  # x, y, self.get_zoom(x,y,self.image.dimension_x, self.image.dimension_y)

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
