from typing import Literal, Optional, Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints, Field, AliasChoices, ValidationError, field_validator, model_validator
from pydantic.functional_validators import BeforeValidator
from api.models import ImageType

from core.db import foreign_key

from core.utils import to_camel

def camel_alias_generator(basename: str):
    def _to_camel(alias: str) -> str:
        if alias == 'id':
            return f'{basename}_id'
        return alias # to_camel(alias)
    return _to_camel

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
tag_alias = camel_alias_generator('tag')

class TagBase(BaseModel):
    """Shared properties."""
    tag: Annotated[str, StringConstraints(to_lower=True)]
    
    model_config=ConfigDict(alias_generator=tag_alias, populate_by_name=True)

class TagCreate(TagBase):
    """Properties to receive on item creation."""
    ...

class TagUpdate(TagBase):
    """Properties to receive on item update. Don't need id, as PUTting to /parents/{id}"""
    ...

class TagInDB(TagBase):
    """Properties shared by models stored in DB - !exposed in create/update."""
    id: foreign_key #= Field(validation_alias=AliasChoices("tag_id", "tagId"))

class Tag(TagInDB):
    """Properties to return to client"""
    model_config=ConfigDict(from_attributes=True,alias_generator=tag_alias,populate_by_name=True)
    #
class TagById(BaseModel):
    id: foreign_key
    model_config=ConfigDict(from_attributes=True,alias_generator=tag_alias,populate_by_name=True)    

############### Image

image_alias = camel_alias_generator('image')

class ImageBase(BaseModel):
    """Shared properties."""
    name: Optional[str] = ""
    focus_x: Optional[int] = None
    focus_y: Optional[int] = None
    hash: Optional[str] = None
    dimension_x: Optional[int] = None
    dimension_y: Optional[int] = None
    type: Optional[ImageType] = None

    model_config=ConfigDict(alias_generator=image_alias, populate_by_name=True)
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
    path: str
    name: str

class ImageUpdate(ImageBase):
    ...

class Image(ImageBase):
    id: foreign_key
    tags: list["Tag"]

    model_config=ConfigDict(from_attributes=True,alias_generator=image_alias, populate_by_name=True)

class ImageB64(Image):
    ...
    b64: str

class ImageScale(BaseModel):
    width: Optional[int] = None
    height: Optional[int] = None
    scale: Optional[float] = None

    @model_validator(mode='after')
    def check_appropriate_params(self) -> 'ImageScale':
        if (self.width or self.height) and self.scale:
            raise ValidationError #("Cannot supply scale and width or height")
        return self

class TagList(BaseModel):
    tags: list[foreign_key]

    # @field_validator('tags')
    # def split_csv_to_list(cls, field):
    #     if isinstance(field, str):
    #         return [] if field == "" else [int(i) for i in field.split(',')]
    #     return field

class ImageMatch(BaseModel):
    image: 'Image'
    image_id: foreign_key
    match_count: int
    tags: list[foreign_key]

class ImageMatchResult(BaseModel):
    matches: list['ImageMatch']
    tags: list[foreign_key]



############### Directory 

directory_alias = camel_alias_generator('directory')

class DirectoryBase(BaseModel):
    path: str
    model_config=ConfigDict(alias_generator=directory_alias, populate_by_name=True)

class DirectoryUpdate(DirectoryBase):
    ...

class DirectoryCreate(DirectoryBase):
    ...

class Directory(DirectoryBase):
    id: foreign_key
    model_config=ConfigDict(alias_generator=directory_alias, populate_by_name=True)

######################### Message
message_alias = camel_alias_generator('message')
class MessageBase(BaseModel):
    message: str = ""
    model_config=ConfigDict(alias_generator=message_alias, populate_by_name=True)

class MessageUpdate(MessageBase):
    ...

class MessageCreate(MessageBase):
    ...

class Message(MessageBase):
    id: foreign_key
    model_config=ConfigDict(from_attributes=True,alias_generator=message_alias, populate_by_name=True)


###################### Session
session_alias = camel_alias_generator('session')

class SessionBase(BaseModel):
    title: Optional[str] = ""
    image_id: Optional[foreign_key] = None
    message_id: Optional[foreign_key] = None
    combat_id: Optional[foreign_key] = None
    mode: Literal['loading','backdrop','combat'] = 'loading'
    model_config=ConfigDict(alias_generator=session_alias, populate_by_name=True)

    
class SessionUpdate(SessionBase):
    ...

class SessionCreate(SessionBase):
    ...

class Session(SessionBase):
    id: foreign_key
    
    model_config=ConfigDict(from_attributes=True,alias_generator=session_alias, populate_by_name=True)


########################## Participant
participant_alias = camel_alias_generator('participant')
class ParticipantBase(BaseModel):
    name: Optional[str] = ""
    combat_id: Optional[foreign_key] = None
    entity_id: Optional[foreign_key] = None
    image_id: Optional[foreign_key] = None
    is_visible: Optional[bool] = True 
    is_PC: Optional[bool] = False
    damage: Optional[int] = 0
    max_hp: Optional[int] = 0
    ac: Optional[int] = 10
    initiative: Optional[int] = 10
    initiative_modifier: Optional[int] = 0
    conditions: Optional[str] = [] # list[str]
    has_reaction: Optional[bool] = True
    colour: Optional[str] = ""

    # @field_validator("conditions")
    # def split_csv_to_list(cls, field):
    #     if isinstance(field, str):
    #         return [] if field == "" else field.split(',')
    #     return field
    
    model_config=ConfigDict(alias_generator=participant_alias, populate_by_name=True)


class ParticipantUpdate(ParticipantBase):
    ...

class ParticipantCreate(ParticipantBase):
    ...

class Participant(ParticipantBase):
    id: foreign_key
   
    model_config=ConfigDict(from_attributes=True,alias_generator=participant_alias, populate_by_name=True)


########################## Combat
combat_alias = camel_alias_generator('combat')
class CombatBase(BaseModel):
    title: Optional[str] = ""
    
    model_config=ConfigDict(alias_generator=combat_alias, populate_by_name=True)

class CombatUpdate(CombatBase):
    ...

class CombatCreate(CombatBase):
    title: Optional[str]

class Combat(CombatBase):
    id: foreign_key
    participants: list['Participant']
    
    model_config=ConfigDict(from_attributes=True,alias_generator=combat_alias, populate_by_name=True)

######################## Entity
entity_alias = camel_alias_generator('entity')
class EntityBase(BaseModel):
    name: Optional[str] = ""
    image_id: Optional[foreign_key] = None
    is_PC: Optional[bool] = False
    hit_dice: Optional[str] = ""
    ac: Optional[int] = 10
    cr: Optional[str] = "0"
    initiative_modifier: Optional[int] = 0
    source: Optional[str] = None
    source_page: Optional[int] = None
    
    model_config=ConfigDict(alias_generator=entity_alias, populate_by_name=True)


class EntityUpdate(EntityBase):
    ...

class EntityCreate(EntityBase):
    ...

class Entity(EntityBase):
    id: foreign_key
   
    model_config=ConfigDict(from_attributes=True,alias_generator=entity_alias, populate_by_name=True)
