from typing import Optional

from pydantic import BaseModel

from core.db import foreign_key

from core.utils import to_camel


############### Image

class ImageBase(BaseModel):
    filename: str
    focus_x: Optional[int]
    focus_y: Optional[int]
    dimension_x: int
    dimension_y: int
    directory_id: foreign_key

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True

class ImageUpdate(ImageBase):
    filename: Optional[str]
    dimension_x: Optional[int]
    dimension_y: Optional[int]
    directory_id: Optional[foreign_key]

class ImageCreate(ImageBase):
    ...

class Image(ImageBase):
    id: foreign_key
    hash: str
    tags: list["Tag"]

    class Config:
        orm_mode: True

############### Directory 

class DirectoryBase(BaseModel):
    path: str
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True

class DirectoryUpdate(DirectoryBase):
    ...

class DirectoryCreate(DirectoryBase):
    ...

class Directory(DirectoryBase):
    id: foreign_key
    class Config:
        orm_mode: True

###################### Tag

class TagBase(BaseModel):
    tag: str
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True

class TagUpdate(TagBase):
    ...

class TagCreate(TagBase):
    ...

class Tag(TagBase):
    id: foreign_key
    class Config:
        orm_mode: True

######################### Message

class MessageBase(BaseModel):
    message: str
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True

class MessageUpdate(MessageBase):
    ...

class MessageCreate(MessageBase):
    ...

class Message(MessageBase):
    id: foreign_key
    class Config: 
        orm_mode: True