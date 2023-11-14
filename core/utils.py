import enum
import random
import re
from datetime import date, datetime
from typing import Union


# https://towardsdatascience.com/detection-of-duplicate-images-using-image-hash-functions-4d9c53f04a75
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


class DiceRoll(enum.Enum):
    min = "min"
    max = "max"
    avg = "avg"
    rnd = "rnd"
    one = "one"


def roll(hit_dice: str, mode: DiceRoll = DiceRoll.avg):
    pattern = r"(\d+)d(\d+)\s*\+\s*(\d+)"
    if (a := re.match(pattern, hit_dice)) is None:
        return 0
    try:
        n, d, c = [int(i) for i in a.groups()]
    except Exception:
        return 0
    match mode:
        case DiceRoll.min:
            return n + c
        case DiceRoll.max:
            return n * d + c
        case DiceRoll.avg:
            return int(n * (d + 1) / 2) + c
        case DiceRoll.rnd:
            return sum(random.randint(1, d) for _ in range(n)) + c
        case DiceRoll.one:
            return 1


def produce_readable_error(error_msg: dict) -> str:
    d = {
        "type": "literal_error",
        "loc": ["body", "_SessionEmpty", "mode"],
        "msg": "Input should be <SessionMode.empty: 'empty'>",
        "input": "empty",
        "ctx": {"expected": "<SessionMode.empty: 'empty'>"},
        "url": "https://errors.pydantic.dev/2.4/v/literal_error",
    }
    error = f"Error {error_msg['type']} encountered in request {error_msg['loc'][0]}: {error_msg['loc'][1]}.{error_msg['loc'][2]}.\n"
    detail = f"Field {error_msg['loc'][2]} but instead "
    return ""


def build_stub(i: int) -> str:
    # adj =
    return ""


def rgb_to_hex(rgb) -> str:
    h = lambda x: f"{hex(x)[2:]:0>2}"  # noqa: E731
    return f'#{"".join(map(h, rgb))}'


def hex_to_rgb(hexstr: str) -> tuple:
    if hexstr.startswith("#"):
        hexstr = hexstr[1:]
    h = lambda x: int(x, base=16)  # noqa: E731
    return tuple(h(hexstr[2 * i : 2 * i + 2]) for i in range(3))
