import re

opinions = []
sizes = []
qualities = []
shapes = []
ages = []
colours = []
origins = []
materials = []
types = []
purposes = []
nouns = []


opinions = [
    "amazing",
    "amusing",
    "awful",
    "bad",
    "boring",
    "brilliant",
    "cheeky",
    "correct",
    "delightful",
    "effective",
    "enjoyable",
    "entertaining",
    "excellent",
    "exciting",
    "fantastic",
    "fascinating",
    "fine",
    "funny",
    "good",
    "grand",
    "great",
    "horrible",
    "incredible",
    "interesting",
    "lovely",
    "magnificent",
    "marvellous",
    "nice",
    "outstanding",
    "perfect",
    "pleasant",
    "remarkable",
    "right",
    "rude",
    "silly",
    "spectacular",
    "superb",
    "terrible",
    "terrific",
    "thrilling",
    "tremendous",
    "useful",
    "valuable",
    "wonderful",
    "wrong",
]

# baby 	illimitable 	scrawny
# beefy 	immeasurable 	short
# big 	immense 	sizable
# bony 	infinitesimal 	skeletal
# boundless 	lanky 	skimpy
# brawny 	large 	skinny
# broad 	lean 	slender
# bulky 	life-size 	slim
# chunky 	limitless 	small
# colossal 	little 	squat
# compact 	mammoth 	stocky
# corpulent 	massive 	stout
# cosmic 	meager 	strapping
# cubby 	measly 	sturdy
# curvy 	microscopic 	tall
# elfin 	mini 	teensy
# emaciated 	miniature 	teeny
# endless 	minuscule
# enormous 	minute
# epic 	narrow 	thick
# expansive 	obese 	thickset
# extensive 	outsized 	thin
# fat 	oversize 	tiny
# fleshy 	overweight 	titanic
# full-size 	paltry 	towering
# gargantuan 	petite 	trifling
# gaunt 	pint-size 	trim
# giant 	plump 	tubby
# gigantic 	pocket-size 	undersized
# grand 	portly 	underweight
# great 	pudgy 	unlimited
# heavy 	puny 	vast
# hefty 	rotund 	wee
# huge 	scanty 	whopping
# hulking 	scraggy 	wide


def index_to_stub(i: int) -> str:
    return ""


def split(stub: str) -> list[str]:
    return []


def f1(ini_str) -> list[str]:
    res_list = re.findall("[A-Z][^A-Z]*", ini_str)
    return res_list


# def f2(ini_str) -> list[str]:
#     return [s for s in re.split("([A-Z][^A-Z]*)", ini_str) if s]


# def f3(ini_str) -> list[str]:
#     res_pos = [i for i, e in enumerate(ini_str + "A") if e.isupper()]
#     res_list = [ini_str[res_pos[j] : res_pos[j + 1]] for j in range(len(res_pos) - 1)]
#     return res_list


# def f4(ini_str) -> list[str]:
#     res = ""
#     for i in ini_str:
#         if i.isupper():
#             res += "*" + i
#         else:
#             res += i
#     x: list[str] = res.split("*")
#     x.remove("")
#     return x


# def f5(ini_str) -> list[str]:
#     res = ""
#     for i in ini_str:
#         if ord(i) in range(65, 91):
#             res += "*" + i
#         else:
#             res += i
#     x: list[str] = res.split("*")
#     x.remove("")
#     return x


# def f6(ini_str) -> list[str]:
#     upperalphabets = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
#     # Splitting on UpperCase
#     res = ""
#     for i in ini_str:
#         if i in upperalphabets:
#             res += "*" + i
#         else:
#             res += i
#     x: list[str] = res.split("*")
#     x.remove("")
#     return x


# def f7(ini_str) -> list[str]:
#     upperalphabets = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
#     # Splitting on UpperCase
#     res = ""
#     for i in ini_str:
#         if operator.countOf(upperalphabets, i) > 0:
#             res += "*" + i
#         else:
#             res += i
#     x: list[str] = res.split("*")
#     x.remove("")
#     return x


# if __name__ == "__main__":
#     import timeit

#     print(
#         timeit.timeit(
#             'f1("AwkwardAngularAncientAfghaniAardvarks")',
#             setup="from stub_generator import f1",
#             number=100000,
#         )
#     )
#     print(
#         timeit.timeit(
#             'f2("AwkwardAngularAncientAfghaniAardvarks")',
#             setup="from stub_generator import f2",
#             number=100000,
#         )
#     )
#     print(
#         timeit.timeit(
#             'f3("AwkwardAngularAncientAfghaniAardvarks")',
#             setup="from stub_generator import f3",
#             number=100000,
#         )
#     )
#     print(
#         timeit.timeit(
#             'f4("AwkwardAngularAncientAfghaniAardvarks")',
#             setup="from stub_generator import f4",
#             number=100000,
#         )
#     )
#     print(
#         timeit.timeit(
#             'f5("AwkwardAngularAncientAfghaniAardvarks")',
#             setup="from stub_generator import f5",
#             number=100000,
#         )
#     )
#     print(
#         timeit.timeit(
#             'f6("AwkwardAngularAncientAfghaniAardvarks")',
#             setup="from stub_generator import f6",
#             number=100000,
#         )
#     )
#     print(
#         timeit.timeit(
#             'f7("AwkwardAngularAncientAfghaniAardvarks")',
#             setup="from stub_generator import f7",
#             number=100000,
#         )
#     )
