import enum
from typing import Annotated, Literal, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    StringConstraints,
    ValidationError,
    model_validator,
)

from api.models import ImageType
from core.db import foreign_key


def camel_alias_generator(basename: str):
    def _to_camel(alias: str) -> str:
        if alias == "id":
            return f"{basename}_id"
        return alias  # to_camel(alias)

    return _to_camel


# https://stackoverflow.com/questions/73122511/flask-sqlalchemy-dict-object-has-no-attribute-sa-instance-state
def is_pydantic(obj: object) -> bool:
    """Checks whether an object is pydantic."""
    return type(obj).__class__.__name__ == "ModelMetaclass"


def model_to_entity(schema):
    """
    Iterates through pydantic schema and parses nested schemas
    to a dictionary containing SQLAlchemy models.
    Only works if nested schemas have specified the Meta.orm_model.
    """
    if is_pydantic(schema):
        try:
            converted_model = model_to_entity(dict(schema))
            return schema.Meta.orm_model(**converted_model)

        except AttributeError:
            model_name = schema.__class__.__name__
            raise AttributeError(
                f"Failed converting pydantic model: {model_name}.Meta.orm_model not specified."
            )

    elif isinstance(schema, list):
        return [model_to_entity(model) for model in schema]

    elif isinstance(schema, dict):
        for key, model in schema.items():
            schema[key] = model_to_entity(model)

    return schema


########## EXAMPLE
# class ParentBase(BaseModel):
#     """Shared properties."""
#     name: str
#     email: str

# class ParentCreate(ParentBase):
#     """Properties to receive on item creation."""
#     # dont need id here if your db autocreates it
#     pass

# class ParentUpdate(ParentBase):
#     """Properties to receive on item update."""
#     # dont need id as you are likely PUTing to /parents/{id}
#     # other fields should not be optional in a PUT
#     # maybe what you are wanting is a PATCH schema?
#     pass

# class ParentInDBBase(ParentBase):
#     """Properties shared by models stored in DB - !exposed in create/update."""
#     # primary key exists in db, but not in base/create/update
#     id: int

# class Parent(ParentInDBBase):
#     """Properties to return to client."""
#     # optionally include things like relationships returned to consumer
#     # related_things: List[Thing]
#     pass

# class ParentInDB(ParentInDBBase):
#     """Additional properties stored in DB."""
#     # could be secure things like passwords?
#     pass

########## /END EXAMPLE


class BaseFilter(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageFilter(BaseFilter):
    message: Optional[str] = ""


class TagFilter(BaseFilter):
    tag: Optional[str] = ""


class EntityFilter(BaseFilter):
    name: Optional[str] = ""
    is_PC: Optional[bool] = None


class CombatFilter(BaseFilter):
    title: Optional[str] = ""


class ImageFilter(BaseFilter):
    type: Optional[ImageType] = None
    types: Optional[str] = None
    # taglist: Optional[list[int]] = Query(default=None)


class CollectionFilter(BaseFilter):
    name: Optional[str] = None


#################### TAgs


tag_alias = camel_alias_generator("tag")


class TagBase(BaseModel):
    """Shared properties."""

    tag: Annotated[str, StringConstraints(to_lower=True)]

    model_config = ConfigDict(alias_generator=tag_alias, populate_by_name=True)


class TagCreate(TagBase):
    """Properties to receive on item creation."""

    ...


class TagUpdate(TagBase):
    """Properties to receive on item update. Don't need id, as PUTting to /parents/{id}"""

    ...


class TagInDB(TagBase):
    """Properties shared by models stored in DB - !exposed in create/update."""

    id: foreign_key  # = Field(validation_alias=AliasChoices("tag_id", "tagId"))


class Tag(TagInDB):
    """Properties to return to client"""

    model_config = ConfigDict(
        from_attributes=True, alias_generator=tag_alias, populate_by_name=True
    )
    #


class TagById(BaseModel):
    id: foreign_key
    model_config = ConfigDict(
        from_attributes=True, alias_generator=tag_alias, populate_by_name=True
    )


############### Collections


collection_alias = camel_alias_generator("collection")


class CollectionBase(BaseModel):
    """Shared properties."""

    name: str

    model_config = ConfigDict(alias_generator=collection_alias, populate_by_name=True)


class CollectionCreate(CollectionBase):
    """Properties to receive on item creation."""

    ...


class CollectionUpdate(CollectionBase):
    """Properties to receive on item update. Don't need id, as PUTting to /parents/{id}"""

    ...


class CollectionInDB(CollectionBase):
    """Properties shared by models stored in DB - !exposed in create/update."""

    id: foreign_key


############### Image

image_alias = camel_alias_generator("image")


class ImageBase(BaseModel):
    """Shared properties."""

    name: Optional[str] = ""
    focus_x: Optional[int] = None
    focus_y: Optional[int] = None
    hash: Optional[str] = None
    dimension_x: Optional[int] = None
    dimension_y: Optional[int] = None
    type: Optional[ImageType] = None

    model_config = ConfigDict(alias_generator=image_alias, populate_by_name=True)
    # class Config:
    #     alias_generator = to_camel
    #     allow_population_by_field_name = True


class ImageCreate(ImageBase):
    """Properties to receive on item creation."""

    focus_x: Optional[int] = None
    focus_y: Optional[int] = None
    hash: Optional[str]
    dimension_x: int
    dimension_y: int
    # path: str
    name: str


class ImageUpload(BaseModel):
    name: str
    type: Optional[ImageType] = ImageType.character


class ImageUpdate(BaseModel):
    name: Optional[str] = None
    focus_x: Optional[int] = None
    focus_y: Optional[int] = None
    dimension_x: Optional[int] = None
    dimension_y: Optional[int] = None
    # path: Optional[str] = None
    type: Optional[ImageType] = None


class Image(ImageCreate):
    id: foreign_key
    tags: list["Tag"]
    # collections: list["CollectionInDB"]
    palette: Optional[str] = ""

    model_config = ConfigDict(
        from_attributes=True, alias_generator=image_alias, populate_by_name=True
    )


class ImageURL(Image):
    url: str  # = "None"
    thumbnail_url: str  # = "None"


class Collection(CollectionInDB):
    """Properties to return to client"""

    images: list["ImageURL"]

    model_config = ConfigDict(
        from_attributes=True, alias_generator=collection_alias, populate_by_name=True
    )
    #


# class ImageCreateData(BaseModel):
#     id: foreign_key
#     name: str
#     data: str
#     tags: list["Tag"]

#     model_config = ConfigDict(
#         from_attributes=True, alias_generator=image_alias, populate_by_name=True
#     )


# @model_validator(mode="before")
# @classmethod
# def inject_urls(cls, data: Any) -> Any:
#     #def add_urls(router: APIRouter, **context):
#     url = router.url_path_for('get_full_image', **context)
#     thumbnail_url = router.url_path_for('get_full_image', **context)
#     return data


class ImageB64(Image):
    ...
    b64: Optional[str]


class ImageScale(BaseModel):
    width: Optional[int] = None
    height: Optional[int] = None
    scale: Optional[float] = None

    @model_validator(mode="after")
    def check_appropriate_params(self) -> "ImageScale":
        if (self.width or self.height) and self.scale:  # Given width/height and scale
            raise ValidationError
        if not (self.width and self.height and self.scale):
            self.width = 400
        return self


class TagList(BaseModel):
    tags: list[foreign_key]

    # @field_validator('tags')
    # def split_csv_to_list(cls, field):
    #     if isinstance(field, str):
    #         return [] if field == "" else [int(i) for i in field.split(',')]
    #     return field


class ImageMatch(BaseModel):
    image: "ImageURL"
    image_id: foreign_key
    match_count: int
    tags: list[foreign_key]


class ImageMatchResult(BaseModel):
    matches: list["ImageMatch"]
    tags: list[foreign_key]


######################### Message
message_alias = camel_alias_generator("message")


class MessageBase(BaseModel):
    message: str = ""
    model_config = ConfigDict(alias_generator=message_alias, populate_by_name=True)


class MessageUpdate(MessageBase):
    ...


class MessageCreate(MessageBase):
    ...


class Message(MessageBase):
    id: foreign_key
    message: str
    model_config = ConfigDict(
        from_attributes=True, alias_generator=message_alias, populate_by_name=True
    )


########################## Participant
participant_alias = camel_alias_generator("participant")


class ParticipantBase(BaseModel):
    name: Optional[str] = ""
    #    combat_id: foreign_key

    # @field_validator("conditions")
    # def split_csv_to_list(cls, field):
    #     if isinstance(field, str):
    #         return [] if field == "" else field.split(',')
    #     return field

    model_config = ConfigDict(alias_generator=participant_alias, populate_by_name=True)


class ParticipantUpdate(BaseModel):
    name: Optional[str] = None
    entity_id: Optional[foreign_key] = None
    image_id: Optional[foreign_key] = None
    is_visible: Optional[bool] = None
    is_PC: Optional[bool] = None
    damage: Optional[int] = None
    max_hp: Optional[int] = None
    hit_dice: Optional[str] = None
    ac: Optional[int] = None
    initiative: Optional[int] = None
    initiative_modifier: Optional[int] = None
    conditions: Optional[str] = None
    has_reaction: Optional[bool] = None
    colour: Optional[str] = None


class ParticipantUpdateID(ParticipantUpdate):
    id: foreign_key
    model_config = ConfigDict(
        from_attributes=True, alias_generator=participant_alias, populate_by_name=True
    )


class ParticipantCreate(ParticipantBase):
    entity_id: Optional[foreign_key] = None
    image_id: Optional[foreign_key] = None
    is_visible: bool = True
    is_PC: bool = False
    damage: int = 0
    max_hp: Optional[int] = None
    hit_dice: Optional[str] = None
    ac: int = 10
    initiative: Optional[int] = None
    initiative_modifier: int = 0
    conditions: str = ""  # list[str]
    has_reaction: bool = True
    colour: Optional[str] = ""


class Participant(ParticipantBase):
    id: foreign_key
    combat_id: foreign_key
    name: str
    entity_id: Optional[foreign_key]
    # entity: Optional["Entity"]
    image_id: Optional[foreign_key]
    is_visible: bool
    is_PC: bool
    damage: int
    max_hp: Optional[int] = None
    hit_dice: Optional[str]
    ac: int
    initiative: Optional[int] = None
    initiative_modifier: int
    conditions: str
    has_reaction: bool
    colour: Optional[str]

    model_config = ConfigDict(
        from_attributes=True, alias_generator=participant_alias, populate_by_name=True
    )


########################## Combat
combat_alias = camel_alias_generator("combat")


class CombatBase(BaseModel):
    title: str  # = ""
    active_participant_id: Optional[int] = None
    is_active: Optional[bool] = False

    model_config = ConfigDict(alias_generator=combat_alias, populate_by_name=True)


class CombatUpdate(CombatBase):
    title: Optional[str] = None
    active_participant_id: Optional[int] = None
    is_active: Optional[bool] = None
    participants: Optional[list["ParticipantUpdateID"]] = None
    round: Optional[int] = 0


class CombatCreate(CombatBase):
    title: str
    participants: Optional[list["ParticipantCreate"]] = []


class Combat(CombatBase):
    id: foreign_key
    participants: list["Participant"]
    round: int
    active_participant_id: Optional[int] = None
    is_active: bool = False
    model_config = ConfigDict(
        from_attributes=True, alias_generator=combat_alias, populate_by_name=True
    )


######################## Entity
entity_alias = camel_alias_generator("entity")


class EntityBase(BaseModel):
    name: str = ""
    image_id: Optional[foreign_key] = None
    is_PC: bool = False
    hit_dice: str = ""
    ac: int = 10
    cr: str = "0"
    initiative_modifier: int = 0
    source: Optional[str] = None
    source_page: Optional[int] = None
    # data: Optional[bytes] = None

    model_config = ConfigDict(alias_generator=entity_alias, populate_by_name=True)


class EntityUpdate(EntityBase):
    name: Optional[str] = None
    image_id: Optional[foreign_key] = None
    is_PC: Optional[bool] = None
    hit_dice: Optional[str] = None
    ac: Optional[int] = None
    cr: Optional[str] = None
    initiative_modifier: Optional[int] = None
    source: Optional[str] = None
    source_page: Optional[int] = None


class EntityCreate(EntityBase):
    ...


class Entity(EntityBase):
    id: foreign_key
    data: Optional[bytes]

    model_config = ConfigDict(
        from_attributes=True, alias_generator=entity_alias, populate_by_name=True
    )

    # @model_validator(mode="before")
    # @classmethod
    # def convert_to_json(cls, data):
    #     # try:
    #     if data.data is not None and not isinstance(data.data, dict):
    #         data.data = json.loads(data.data)
    #     elif isinstance(data.data, dict):
    #         pass
    #     else:
    #         data.data = {}

    #     # except Exception:
    #     return data


###################### Session
session_alias = camel_alias_generator("session")


# class aSessionBase(BaseModel):
#     title: Optional[str] = ""
#     backdrop_id: Optional[foreign_key] = None
#     overlay_image_id: Optional[foreign_key] = None
#     message_id: Optional[foreign_key] = None
#     combat_id: Optional[foreign_key] = None
#     mode: Optional[SessionMode] = SessionMode.backdrop

#     model_config = ConfigDict(alias_generator=session_alias, populate_by_name=True)


# class aSessionUpdate(aSessionBase):
#     ...


# class aSessionCreate(aSessionBase):
#     ...


# class aSession(aSessionBase):
#     id: foreign_key
#     backdrop: Optional["ImageURL"] = None
#     overlay_image: Optional["ImageURL"] = None
#     message: Optional["Message"] = None
#     combat: Optional["Combat"] = None

#     model_config = ConfigDict(
#         from_attributes=True, alias_generator=session_alias, populate_by_name=True
#     )


# class SessionState(enum.Enum):
#     loading = "loading"
#     error = "error"
#     done = "done"


# class _LoadingSession(BaseModel):
#     state: Literal[SessionState.loading]


# class _ErrorSession(BaseModel):
#     state: Literal[SessionState.error]
#     error: Any


class SessionEmpty(BaseModel):
    mode: Literal["empty"] = "empty"
    title: str = ""

    model_config = ConfigDict(
        from_attributes=True, alias_generator=session_alias, populate_by_name=True
    )


class SessionBackdrop(SessionEmpty):
    mode: Literal["backdrop"]
    backdrop_id: Optional[foreign_key]


class SessionLoading(SessionBackdrop):
    mode: Literal["loading"]
    message_id: Optional[foreign_key]


class SessionCombat(SessionBackdrop):
    mode: Literal["combat"]
    combat_id: foreign_key


class SessionHandout(SessionBackdrop):
    mode: Literal["handout"]
    overlay_image_id: foreign_key


class SessionMap(SessionHandout):
    mode: Literal["map"]


SessionCreate = (
    SessionEmpty | SessionBackdrop | SessionLoading | SessionCombat | SessionHandout | SessionMap
)
##############################################


class SessionUpdate(BaseModel):
    mode: Literal["empty"] | Literal["loading"] | Literal["backdrop"] | Literal[
        "overlay"
    ] | Literal["map"] = "empty"
    title: Optional[str] = ""
    backdrop_id: Optional[foreign_key] = None
    combat_id: Optional[foreign_key] = None
    message_id: Optional[foreign_key] = None
    overlay_image_id: Optional[foreign_key] = None

    model_config = ConfigDict(
        from_attributes=True, alias_generator=session_alias, populate_by_name=True
    )


##############################################
class SessionEmptyId(BaseModel):
    mode: Literal["empty"]
    title: str = ""
    id: foreign_key
    ws_url: str

    model_config = ConfigDict(
        from_attributes=True, alias_generator=session_alias, populate_by_name=True
    )


class SessionBackdropId(SessionEmptyId):
    mode: Literal["backdrop"]
    backdrop: "ImageURL"
    backdrop_id: foreign_key


class SessionLoadingId(SessionBackdropId):
    mode: Literal["loading"]
    message: "Message"
    message_id: foreign_key


class SessionCombatId(SessionBackdropId):
    mode: Literal["combat"]
    combat: "Combat"
    combat_id: foreign_key


class SessionHandoutId(SessionBackdropId):
    mode: Literal["handout"]
    overlay_image: "ImageURL"
    overlay_image_id: foreign_key


class SessionMapId(SessionHandoutId):
    mode: Literal["map"]


Session = (
    SessionEmptyId
    | SessionBackdropId
    | SessionLoadingId
    | SessionCombatId
    | SessionHandoutId
    | SessionMapId
)

################################


class WSEventType(enum.Enum):
    session_updated = "session_updated"
    show_message = "show_message"


class WSEventUpdate(BaseModel):
    event: Literal[WSEventType.session_updated]
    paylod: None


class _WSEventMessagePayload(BaseModel):
    message: str
    timeout: Optional[int]


class WSEventMessage(BaseModel):
    event: Literal[WSEventType.show_message]
    payload: _WSEventMessagePayload


WSEvent = WSEventUpdate | WSEventMessage


class WSPub(BaseModel):
    channel: int
    event: WSEvent
