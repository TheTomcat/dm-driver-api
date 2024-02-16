import enum
import random
import re
from datetime import date, datetime
from typing import Optional, Union


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


CHARS = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def make_seq(i: Optional[int] = None, length=16) -> str:
    r = random.Random(i)
    return "".join(r.choices(CHARS, k=length))


def rgb_to_hex(rgb) -> str:
    h = lambda x: f"{hex(x)[2:]:0>2}"  # noqa: E731
    return f'#{"".join(map(h, rgb))}'


def hex_to_rgb(hexstr: str) -> tuple:
    if hexstr.startswith("#"):
        hexstr = hexstr[1:]
    h = lambda x: int(x, base=16)  # noqa: E731
    return tuple(h(hexstr[2 * i : 2 * i + 2]) for i in range(3))


# DECODECR = {i: f"{i}" for i in range(31)}
# DECODECR.update({-1: "1/2", -2: "1/4", -3: "1/8"})
# ENCODECR = {val: key for key, val in DECODECR.items()}


def decodeCR(cr_DB: float | None) -> str | None:
    """Take a float from the set {0, 0.125, 0.25, 0.5, 1, ... ,31}
    and return its corresponding CR. Returns None otherwise"""
    if cr_DB is None:
        return None
    cr_int = int(cr_DB)
    if cr_int == cr_DB and 0 <= cr_int <= 31:
        return f"{cr_int}"
    if 0 < cr_DB < 1:
        cr_inverse = int(1 / cr_DB)
        if cr_inverse in [2, 4, 8]:
            return f"1/{cr_inverse}"
    return None
    # return DECODECR.get(cr_DB, None)


def encodeCR(cr_str: str | None) -> float | None:
    """Take a CR in string form (either an int or 1/int) and return the float"""
    if cr_str is None or cr_str == "":
        return None
    match cr_str:
        case "1/8":
            return 0.125
        case "1/4":
            return 0.25
        case "1/2":
            return 0.5
    if cr_str == f"{int(cr_str)}":
        return int(cr_str)

    # return ENCODECR.get(cr_str, None)


def validateCR():  # Test suite
    test = [i for i in range(31)]
    test = [0.125, 0.25, 0.5, *test]
    out = [decodeCR(i) for i in test]
    out2 = [encodeCR(i) for i in out]
    return out2 == test


def extract_AC(c: dict) -> int | None:
    ac = c.get("ac", [None])[0]
    if ac is None:
        return None
    if isinstance(ac, int):
        return ac
    if isinstance(ac, dict):
        return ac.get("ac")
    return None


def extract_CR(c: dict) -> float | None:
    cr = c.get("cr")
    if cr is None:
        return None
    if isinstance(cr, str):
        return encodeCR(cr)
    return encodeCR(cr.get("cr"))
