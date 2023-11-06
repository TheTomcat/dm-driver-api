from datetime import date, datetime
from typing import Union


def to_camel(string: str) -> str:
    if "_" not in string:
        return string
    words = string.split("_")
    words = [words[0]] + [word.capitalize() for word in words[1:]]
    return "".join(words)


def to_pascal(string: str) -> str:
    if "_" not in string:
        return string
    words = string.split("_")
    words = [word.capitalize() for word in words]
    return "".join(words)


def datetime_to_string(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def string_to_datetime(st: str) -> datetime:
    return datetime.now()


def string_to_date(st: str) -> date:
    return date(2023, 1, 1)


def url_date_or_datetime_to_obj(date_or_datetime: str) -> Union[date, datetime]:
    # if len(date_or_datetime) == 10:
    #     return date.fromisoformat(date_or_datetime)
    # else:
    return datetime.fromisoformat(date_or_datetime)