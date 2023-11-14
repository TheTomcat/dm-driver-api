from sqlalchemy import Select, select

from api.models import Message, Tag
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
    return q


def _message_like(q: Select, model: Message, param: str) -> Select:
    return q.where(model.message.ilike(f"%{param.lower()}%"))  # type: ignore


def _tag_like(q: Select, model: Tag, param: str) -> Select:
    return q.where(model.tag.ilike(f"%{param.lower()}%"))  # type: ignore


def _name_like(q: Select, model: Tag, param: str) -> Select:
    return q.where(model.name.ilike(f"%{param.lower()}%"))  # type: ignore
