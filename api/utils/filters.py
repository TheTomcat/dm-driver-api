from sqlalchemy import Select, select

from api.models import Image, ImageType, Message, Tag
from api.schemas import BaseFilter


def generate_filter_query(model, filter: BaseFilter) -> Select:
    q = select(model)
    for field, val in filter.model_dump(exclude_defaults=True).items():
        match field:
            case "message":
                q = _message_like(q, model, val)  # type: ignore
            case "tag":
                q = _tag_like(q, model, val)
            case "name":
                q = _name_like(q, model, val)
            case "title":
                q = _title_like(q, model, val)
            case "is_PC":
                q = _is_PC(q, model, val)
            case "type":
                q = _type_is(q, model, val)
    return q


def _message_like(q: Select, model: Message, param: str) -> Select:
    return q.where(model.message.ilike(f"%{param.lower()}%"))  # type: ignore


def _tag_like(q: Select, model: Tag, param: str) -> Select:
    return q.where(model.tag.ilike(f"%{param.lower()}%"))  # type: ignore


def _name_like(q: Select, model: Tag, param: str) -> Select:
    return q.where(model.name.ilike(f"%{param.lower()}%"))  # type: ignore


def _title_like(q: Select, model: Tag, param: str) -> Select:
    return q.where(model.title.ilike(f"%{param.lower()}%"))  # type: ignore


def _is_PC(q: Select, model: Tag, param: str) -> Select:
    return q.where(model.is_PC == param)  # type: ignore


def _type_is(q: Select, model: Image, param: ImageType) -> Select:
    return q.where(model.type == param)  # type: ignore
