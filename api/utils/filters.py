from sqlalchemy import Select, func, select

from api.models import Combat, Entity, Image, ImageType, Message, Participant, Tag
from api.schemas import BaseFilter, SortBy, SortOption


def generate_filter_query(model, filter: BaseFilter) -> Select:
    q = select(model)
    filter_dump = filter.model_dump(exclude_defaults=True)
    if (
        "combat_participants_at_least" in filter_dump
        and "combat_participants_at_most" in filter_dump
    ):
        filter_dump["combat_participants_in_range"] = [
            filter_dump["combat_participants_at_least"],
            filter_dump["combat_participants_at_most"],
        ]
        del filter_dump["combat_participants_at_most"]
        del filter_dump["combat_participants_at_least"]
    for field, val in filter_dump.items():
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
            case "has_image":
                q = _has_image(q, model, val)
            case "has_data":
                q = _has_data(q, model, val)
            case "cr":
                q = _cr_is_one_of(q, model, val)
            case "type":
                q = _type_is(q, model, val)
            case "types":
                q = _type_is_one_of(q, model, val)
            case "combat_participants_at_least":
                q = _combat_participants_at_least(q, model, val)
            case "combat_participants_at_most":
                q = _combat_participants_at_most(q, model, val)
            case "combat_participants_in_range":
                q = _combat_participants_in_range(q, model, val)
            case "combat_participants_name":
                q = _combat_participants_name(q, model, val)
    return q


def _message_like(q: Select, model: Message, param: str) -> Select:
    return q.where(model.message.ilike(f"%{param.lower()}%"))  # type: ignore


def _tag_like(q: Select, model: Tag, param: str) -> Select:
    return q.where(model.tag.ilike(f"%{param.lower()}%"))  # type: ignore


def _name_like(q: Select, model: Tag, param: str) -> Select:
    return q.where(model.name.ilike(f"%{param.lower()}%"))  # type: ignore


def _title_like(q: Select, model: Tag, param: str) -> Select:
    return q.where(model.title.ilike(f"%{param.lower()}%"))  # type: ignore


def _is_PC(q: Select, model: Entity, param: str) -> Select:
    return q.where(model.is_PC == param)  # type: ignore


def _has_image(q: Select, model: Entity, param: bool) -> Select:
    if param:
        return q.where(model.image_id != None)  # type: ignore
    else:
        return q.where(model.image_id == None)  # type: ignore


def _has_data(q: Select, model: Entity, param: bool) -> Select:
    if param:
        return q.where(func.length(model.data) > 4)  # type: ignore
    else:
        return q.where(func.length(model.data) < 4)  # type: ignore


def _cr_is_one_of(q: Select, model: Entity, params: str) -> Select:
    return q.where(model.cr.in_(params.split("|")))  # type: ignore


def _type_is(q: Select, model: Image, param: ImageType) -> Select:
    return q.where(model.type == param)  # type: ignore


def _type_is_one_of(q: Select, model: Image, params: str) -> Select:
    return q.where(model.type.in_(params.split("|")))  # type: ignore


def _combat_participants_at_least(q: Select, model: Combat, params: int) -> Select:
    return q.join(Participant).group_by(Combat.id).having(func.count(Participant.id) >= params)  # type: ignore


def _combat_participants_in_range(q: Select, model: Combat, params: list[int]) -> Select:
    a, b = params
    q_a = func.count(Participant.id) >= a
    q_b = func.count(Participant.id) <= b
    return q.join(Participant).group_by(Combat.id).having(q_a).having(q_b)  # type: ignore


def _combat_participants_at_most(q: Select, model: Combat, params: int) -> Select:
    return q.join(Participant).group_by(Combat.id).having(func.count(Participant.id) <= params)  # type: ignore


def _combat_participants_name(q: Select, model: Combat, params: str) -> Select:
    params_list = params.split("|")

    aggregate = func.aggregate_strings(Participant.name, ";").label("aggregate")
    conditions = [aggregate.ilike(f"%{p}%") for p in params_list]
    # q = q.select(q, aggregate).join(Participant).group_by(Combat.id)
    sq = q.subquery()
    q = (
        select(sq, aggregate)
        .join(Participant, sq.c.id == Participant.combat_id)
        .join(Combat, sq.c.id == Combat.id)
        .group_by(Combat.id)
        .having(*conditions)
    )
    r = q.subquery()
    q = select(Combat).join(r, Combat.id == r.c.id)

    return q


def generate_sort_query(q: Select, model, order: SortBy) -> Select:
    sort_statement = model.id
    match order.sort_by:
        case "title":
            sort_statement = func.lower(model.title)
        case "name":
            sort_statement = func.lower(model.name)
        case "id":
            sort_statement = model.id
        case "num_participants":
            if order.sort_dir == SortOption.desc:
                q = (
                    q.join(Participant)
                    .order_by(func.count(Participant.id).desc())
                    .group_by(Combat.id)
                )
            elif order.sort_dir == SortOption.asc:
                q = (
                    q.join(Participant)
                    .order_by(func.count(Participant.id).asc())
                    .group_by(Combat.id)
                )
            sort_statement = None  # func.count(model.participants)
        case "ac":
            sort_statement = model.ac
        case "cr":
            sort_statement = model.cr
        case "initiative":
            sort_statement = model.initiative_modifier
        case "dimensions":
            sort_statement = model.dimension_x * model.dimension_y
    if order.sort_dir == SortOption.desc and sort_statement is not None:
        sort_statement = sort_statement.desc()
    if order.sort_dir != SortOption.NONE and sort_statement is not None:
        return q.order_by(sort_statement)
    else:
        return q
