import itertools
import json
import os
import pathlib
import shutil
import uuid
from collections import namedtuple
from typing import Annotated, Callable, Iterator, Optional

import typer
from alembic import command
from alembic.config import Config
from PIL import Image as PImage
from rich import print
from rich.progress import Progress, track
from sqlalchemy import select, update

from api.models import Combat, Entity, Image, ImageType, Message, Participant
from core.colour import extract_pallete
from core.session import create_session
from core.utils import make_seq, rgb_to_hex

app = typer.Typer()


def make_print(prefix: str, verbose: bool):
    "Create a prefixed print and input function for scripts."

    def _print(*args, **kwargs):
        """Redifine the print function, suppress output if not in verbose mode, but allow printing via override=True.
        Also adds a prefix as defined earlier, suppress with np=True"""
        override = False
        if kwargs.get("override", False):
            override = True
            del kwargs["override"]
        if verbose or override:
            if kwargs.get("np", False):
                del kwargs["np"]
                print(*args, **kwargs)
                return
            print(f"{prefix}", *args, **kwargs)

    def _input(prompt):
        print(f"{prefix}{prompt}", end="")
        return input()

    return _print, _input


@app.command()
def parse_image_directory(
    directory: Annotated[str, typer.Argument()],
    extensions: Annotated[str, typer.Argument(help="Extensions to parse, comma separated")] = "png",
    image_type: Annotated[
        ImageType, typer.Option(help="The type of image, to store in the database.")
    ] = ImageType.backdrop,
    force_reparse: Annotated[
        bool,
        typer.Option(
            help="If this is true, and an image with the same path and type is found in the database, it will be replaced."
        ),
    ] = False,
    verbose: Annotated[bool, typer.Option(help="Display detailed debugging")] = False,
    recursive: Annotated[bool, typer.Option(help="Search directories recursively")] = False,
    attach_entity: Annotated[
        bool,
        typer.Option(
            help="Attempt to attach any images found to entities within the database based on name"
        ),
    ] = False,
):
    """Parse a directory for image files, and then store them in the database. Optionally attempt to find an entity that matches and link the image to the entity"""
    print, input = make_print("[red]\\[parse-directory][/red]  ", verbose)

    if force_reparse:
        i = input(":fire: Are you sure you want to continue? This may delete data. \[y/N]")
        if i.lower() != "y":
            print("Exiting...")
            return
    path = pathlib.Path(directory)
    db_session = create_session()

    extensions_list = extensions.split(",")
    print(
        f"Now parsing {path} for \[{extensions}]: recursive={recursive}",
        override=True,
    )

    if recursive:
        iterable = multiple_file_types(path.rglob, extensions_list)
    else:
        iterable = multiple_file_types(path.glob, extensions_list)
    if not verbose:
        iterable = track([i for i in iterable], description="Processing...")
    i = 0
    seq = make_seq()
    for image_path in iterable:
        image = db_session.scalar(
            select(Image).where(
                Image.path == str(image_path) and Image.type == image_type  # type: ignore
            )
        )
        if image:
            print(
                f"Found image ([yellow]{image.type.name}[/yellow]) at [green]{image_path}[/green]",
                end="",
            )
            if force_reparse:
                db_session.delete(image)
                print(" - [red]Removing[/red]", np=True)
            else:
                print(" - [yellow]Skipping[/yellow]", np=True)
                continue
        if attach_entity:
            new_image = Image.create_from_local_file(image_path, type=image_type, seq=seq)
            e = db_session.scalar(select(Entity).where(Entity.name.ilike(image_path.stem)))
            if e:
                e.image = new_image
        else:
            new_image = Image.create_from_local_file(image_path, type=image_type, seq=seq)
        db_session.add(new_image)
        i = i + 1
        print(f"Adding image ([yellow]{new_image.type}[/yellow]) at [green]{image_path}[/green]")
    print(f"{i} images parsed <Seq={seq}>", override=True)
    db_session.commit()


@app.command()
def parse_compendium(
    compendium_file: Annotated[str, typer.Argument(help="The file to parse")],
    verbose: Annotated[bool, typer.Option()] = False,
    process_images: Annotated[
        bool,
        typer.Option(
            help="Scan a folder for images that match the name of the monster, and then add them to the database"
        ),
    ] = False,
    image_directory: Annotated[
        Optional[str],
        typer.Argument(
            help="The folder to scan. If not supplied, will attempt to guess the folder (using the usual structure of the 5e.tools codebase)"
        ),
    ] = None,
):
    """Parse a 5e.tools file for entities to store in the database. This is horrible and globby but works for the moment."""
    print, input = make_print("[red]\[parse-compendium][/red] ", verbose)
    db_session = create_session()
    with open(compendium_file, "r") as f:
        data = json.load(f)
    seq = make_seq()

    if process_images and image_directory is None:
        process_images = True
        bestiaryimagepath = pathlib.Path(compendium_file).parent.parent.parent.joinpath(
            pathlib.Path("img\\bestiary")
        )
        if not bestiaryimagepath.is_dir():
            response = input(
                "Unable to automatically detect image directory. Proceed anyway? [Y/n]"
            )
            if response.lower() == "n":
                return
    elif process_images and image_directory is not None:
        bestiaryimagepath = pathlib.Path(image_directory)
        if not bestiaryimagepath.is_dir():
            response = input(
                f"Supplied path {bestiaryimagepath} is not a valid directory. Proceed anyway? [Y/n]"
            )
            if response.lower() == "n":
                return
    else:
        bestiaryimagepath = None

    i = 0
    j = 0
    for monster in track(data["monster"], description="processing"):
        try:
            try:
                cr = (
                    (monster["cr"] if isinstance(monster["cr"], str) else monster["cr"]["cr"])
                    if "cr" in monster
                    else ""
                )
                hit_dice = monster["hp"]["formula"] if "hp" in monster else ""
                ac = find_max(monster, "ac") if "ac" in monster else 0
                init = (monster.get("dex", 10) - 10) // 2 if "dex" in monster else 0
            except KeyError:
                # print(monster, ac, cr, hit_dice, override=True)
                continue
            m = Entity(
                name=monster["name"],
                hit_dice=hit_dice,
                ac=ac,
                cr=cr,
                initiative_modifier=init,
                is_PC=False,
                source=monster["source"],
                source_page=monster["page"],
                data=json.dumps(monster).encode(),
                seq=seq,
            )
            if process_images and monster.get("hasToken", False) and bestiaryimagepath is not None:
                datapath = bestiaryimagepath.joinpath(monster["source"].upper())
                if not datapath.is_dir():
                    continue

                file = list(datapath.glob(f'{monster.get("name")}*'))
                if file:
                    file = file[0]
                    image = Image.create_from_local_file(file, type=ImageType.character, seq=seq)
                    m.image = image
                    db_session.add(image)
                    j = j + 1

        except Exception as e:
            print(monster)
            raise e
        print(f"Parsing {monster['name']}")
        db_session.add(m)
        i = i + 1
    print(f"{i} entites parsed. {j} images created.", override=True)
    db_session.commit()


# @app.command()
# def add_players():
#     "Add in my players"
#     print, input = make_print("[blue]\[add-players][/blue]       ", True)
#     sess = create_session()
#     image_map = (
#         ("Aggie", "D:\\RPGs\\Campaigns\\2\\Aggie.png"),
#         ("Fran", "D:\\RPGs\\Campaigns\\2\\Fran.png"),
#         ("Sorsha", "D:\\RPGs\\Campaigns\\2\\Sorsha.png"),
#         ("Gil", "D:\\RPGs\\Campaigns\\2\\Gilbert.png"),
#     )
#     players = []
#     for name, image in image_map:
#         i = Image.create_from_local_file(pathlib.Path(image), type="character")
#         e = Entity(name=name, initiative_modifier=0, is_PC=True, image=i)
#         players.append(e)
#         sess.add_all([i, e])
#     sess.commit()
#     return players


# @app.command()
# def setup():
#     "Perform a setup for my system"
#     print, input = make_print("[blue]\[sys-setup][/blue]         ", True)
#     images = [
#         # ( ImageType, Path, Recursive Search?, Extensions)
#         ("backdrop", "D:\\RPGs\\Backdrops", False, "png"),
#         ("character", "D:\\RPGs\\Character Images", True, "png,jpg,jpeg"),
#     ]

#     compendia = [
#         "D:\\RPGs\\5e.tools\\5etools-mirror-1.github.io-1.142.0\\data\\bestiary\\bestiary-mm.json",
#         "D:\\RPGs\\5e.tools\\5etools-mirror-1.github.io-1.142.0\\data\\bestiary\\bestiary-mtf.json",
#         "D:\\RPGs\\5e.tools\\5etools-mirror-1.github.io-1.142.0\\data\\bestiary\\bestiary-vgm.json",
#         "D:\\RPGs\\5e.tools\\5etools-mirror-1.github.io-1.142.0\\data\\bestiary\\bestiary-ftd.json",
#     ]

#     players = add_players()

#     for image_type, directory, recursive, extensions in images:
#         parse_directory(directory, extensions, image_type, recursive=recursive)

#     for compendium in compendia:
#         parse_compendium(compendium, process_images=True)

#     load_messages("messages.json")

#     load_tags("tags.json")

#     build_dummy_data(players)

#     generate_tags()


# @app.command()
# def insert_extra_data():
#     compendia = [
#         "D:\\RPGs\\5e.tools\\5etools-mirror-1.github.io-1.142.0\\data\\bestiary\\bestiary-mm.json",
#         "D:\\RPGs\\5e.tools\\5etools-mirror-1.github.io-1.142.0\\data\\bestiary\\bestiary-mtf.json",
#         "D:\\RPGs\\5e.tools\\5etools-mirror-1.github.io-1.142.0\\data\\bestiary\\bestiary-vgm.json",
#         "D:\\RPGs\\5e.tools\\5etools-mirror-1.github.io-1.142.0\\data\\bestiary\\bestiary-ftd.json",
#     ]
#     monsters = []
#     for compendium in compendia:
#         with open(compendium) as f:
#             monsters.extend(json.load(f)["monster"])

#     q = select(Entity).where(Entity.is_PC != True)  # noqa: E712
#     session = create_session()
#     results = session.scalars(q).all()
#     for result in results:
#         m = next(filter(lambda m: m["name"] == result.name, monsters))
#         if m:
#             print(f'Putting {m["name"]} into {result.name}')
#             result.data = json.dumps(m).encode()
#     session.commit()


# @app.command()
# def load_tags(filename):
#     "Load tags from my old version, loading from a json file format [[filename(with extension!), tagname], ...]"
#     print, input = make_print("[red]\[load-tags][/red]        ", True)
#     session = create_session()
#     with open(filename, "r") as f:
#         data = json.load(f)
#     tags: set[str] = set()
#     images: dict[str, Image] = {}
#     for image, tag in data:
#         tags.add(tag)
#         images[image] = session.scalar(select(Image).where(Image.name == image[:-4]))

#     tag_elements: dict[str, Tag] = {}
#     for t in tags:
#         tag_element = session.scalar(select(Tag).where(Tag.tag == t.lower()))
#         if not tag_element:
#             tag_element = Tag(tag=t.lower())
#         tag_elements[t] = tag_element

#     print(f"Found {len(tag_elements)} tags and {len(images)} images, with {len(data)} operations")
#     session.add_all(tag_elements.values())

#     for image, tag in data:
#         images[image].tags.append(tag_elements[tag])

#     session.commit()


def build_dummy_data(players=None):
    print, input = make_print("[magenta]\[build-dummy-data][/magenta] ", True)
    print("Building combats")
    db_session = create_session()

    goblin = db_session.scalar(select(Entity).where(Entity.name == "Goblin"))
    goblin_boss = db_session.scalar(select(Entity).where(Entity.name == "Goblin Boss"))
    hobgoblin = db_session.scalar(select(Entity).where(Entity.name == "Hobgoblin"))

    yeti = db_session.scalar(select(Entity).where(Entity.name == "Yeti"))
    ice_mephit = db_session.scalar(select(Entity).where(Entity.name == "Ice Mephit"))

    c1 = Combat(title="Goblin Fight")
    if players:
        for player in players:
            c1.participants.append(Participant.from_entity(player))
    c1.participants.append(Participant.from_entity(goblin))  # type: ignore
    c1.participants.append(Participant.from_entity(goblin))  # type: ignore
    c1.participants.append(Participant.from_entity(goblin))  # type: ignore
    c1.participants.append(Participant.from_entity(goblin_boss))  # type: ignore
    c1.participants.append(Participant.from_entity(hobgoblin))  # type: ignore
    c1.participants.append(Participant.from_entity(hobgoblin))  # type: ignore

    c2 = Combat(title="Snow Fight")
    if players:
        for player in players:
            c1.participants.append(Participant.from_entity(player))
    c2.participants.append(Participant.from_entity(yeti))  # type: ignore
    c2.participants.append(Participant.from_entity(yeti))  # type: ignore
    c2.participants.append(Participant.from_entity(ice_mephit))  # type: ignore
    c2.participants.append(Participant.from_entity(ice_mephit))  # type: ignore
    c2.participants.append(Participant.from_entity(ice_mephit))  # type: ignore
    c2.participants.append(Participant.from_entity(ice_mephit))  # type: ignore

    db_session.add_all([c1, c2])
    db_session.commit()


# @app.command()
# def generate_tags():
#     "Look in a folder full of images on my computer and try to guess appropriate tags for them, based on subfolders"
#     print, input = make_print("[cyan]\[generate-tags][/cyan]    ", True)
#     base_path = pathlib.Path("D:\\RPGs\\Character Images\\")
#     db_session = create_session()

#     images = db_session.scalars(select(Image).where(Image.path.ilike(f"%{base_path}%"))).all()
#     tag_actions = defaultdict(list)
#     for image in track(images):
#         tags = os.path.normpath(pathlib.Path(image.path).relative_to(base_path)).split(os.sep)
#         for tag in tags[:-1]:
#             tag_actions[tag].append(image.id)
#     print(
#         f'Found {len(tag_actions)} tags: \[{", ".join([f"{tag}: {len(im)}" for tag, im in tag_actions.items()])}]'
#     )
#     for tagname, images in tag_actions.items():
#         if tagname.lower() in [
#             "default",  # Not sure why I made a folder called 'default'.
#             "working wolder",
#             "iacac",
#         ]:
#             continue
#         tag = db_session.scalar(select(Tag).where(Tag.tag == tagname.lower()))
#         if not tag:
#             tag = Tag(tagname)
#             db_session.add(tag)
#             db_session.commit()
#         for im_id in images:
#             db_session.execute(insert(image_tags).values(image_id=im_id, tag_id=tag.id))
#     db_session.commit()

action_row = namedtuple(
    "action_row", ("image_id", "old_path", "new_path", "size", "action")
)  #  'new_name', 'extension', 'type',


@app.command()
def package(
    directory: Annotated[str, typer.Argument(help="The path to output images into")],
    convert_png: Annotated[
        bool,
        typer.Option(help="Convert images to png during the transfer. Not yet implemented."),
    ] = False,
    use_subdir: Annotated[
        bool,
        typer.Option(
            help="Sort images based on their type (backdrop, character etc) into different folders."
        ),
    ] = False,
    create_dir: Annotated[bool, typer.Option(help="Create directory if it does not exist")] = True,
    blind: Annotated[
        bool, typer.Option(help="Run operations without committing changes to the database")
    ] = False,
):
    """Package the database and images to transfer them to another location. Warning, this could take a while"""
    print, input = make_print("[red]\[package][/red]        ", True)
    output_directory = pathlib.Path(directory)
    if not output_directory.is_dir() and not create_dir:
        print(f"Invalid output directory {directory}")
        return
    elif not output_directory.is_dir() and create_dir:
        os.mkdir(output_directory)
    if use_subdir:
        for subdir_stub in ImageType:
            subdir = output_directory.joinpath(subdir_stub.name)
            if not subdir.is_dir() and create_dir:
                os.mkdir(output_directory.joinpath(subdir.name))
            elif not subdir.is_dir():
                print(f"Invalid output directory {subdir}")
                return

    db_session = create_session()
    images = db_session.scalars(select(Image)).all()
    actions = []
    total_size = 0

    for image in track(images, description="Parsing images..."):
        old_path = pathlib.Path(image.path)
        if not old_path.exists():
            print(f"Error parsing <Image id={image.id}>, not found at location {image.path}")
        size = os.path.getsize(old_path)
        new_name = uuid.uuid4()
        extension = (
            old_path.suffix
        )  # image.path.split(".")[-1]  # CONVERT_PNG: #if not convert_png else 'png'
        convert_image = convert_png and extension != ".png"
        if use_subdir:
            new_path = output_directory.joinpath(
                str(image.type.name)
            )  # .joinpath(f"{new_name}{extension}")
        else:
            new_path = output_directory
        new_path = new_path.joinpath(f"{new_name}{'.png' if convert_image else extension}")
        actions.append(
            action_row(
                image_id=image.id,
                old_path=old_path,
                new_path=new_path,
                size=size,
                action="convert" if convert_image else "copy",
            )
        )
        total_size += size
    i = input(
        f"{len(actions)} files will now be {'blindly ' if blind else ''}migrated, total {total_size/1000000:.2f} MBi. Contine? \[y/N] "
    )
    if i.lower() != "y":
        print("Aborting...")
        return
    count = 0
    with Progress() as progress:
        num_files = progress.add_task("[red]Number of files...", total=len(actions))
        total_size = progress.add_task("[green]Total filesize...", total=total_size)

        # Multiprocessing options
        # pool = Pool(8)
        # gen = partial(
        #     perform_operation,
        #     blind=blind,
        #     # session=db_session,
        #     # progress=progress,
        #     # num_files=num_files,
        #     # total_size=total_size,
        # )
        # results = pool.map(gen, actions)

        for image_id, old_path, new_path, size, action in actions:
            count += 1
            if action == "copy":
                shutil.copy(old_path, new_path)
            else:
                with PImage.open(old_path) as f:
                    f.save(new_path)

            if not blind:
                q = update(Image).where(Image.id == image_id).values(path=str(new_path))
                db_session.execute(q)
            progress.update(num_files, advance=1)
            progress.update(total_size, advance=size)
    print(f'{count} images migrated, totalling {total_size/1000000:.2f} MBi."')
    if not blind:
        db_session.commit()


def perform_operation(
    opr,
    blind: bool,
    # session: scoped_session,
    # progress: Progress,
    # num_files: TaskID,
    # total_size: TaskID,
):
    image_id, old_path, new_path, size, action = opr
    if action == "copy":
        shutil.copy(old_path, new_path)
    else:
        with PImage.open(old_path) as f:
            f.save(new_path)
    # if not blind:
    # q = update(Image).where(Image.id == image_id).values(path=str(new_path))
    # session.execute(q)
    # progress.update(num_files, advance=1)
    # progress.update(total_size, advance=size)


@app.command()
def load_messages(
    json_file: Annotated[str, typer.Argument(help="The path of the file to load the messages from")]
):
    print, input = make_print("[green][load-messages][/green]    ", True)
    with open(json_file, "r") as f:
        data = json.load(f)
    print(f"Importing {len(data['payload'])} messages.")
    db_session = create_session()
    for message in data["payload"]:
        m = Message(message=message["message"])
        db_session.add(m)
    db_session.commit()


@app.command()
def generate_colours(
    quality: Annotated[
        int,
        typer.Argument(
            help="quality for the colour thief algorithm (1-10). Lower is slower",
            min=1,
            max=10,
        ),
    ] = 3,
    num_images: Annotated[int, typer.Argument(help="Palette size, default=5")] = 5,
    force_regen: Annotated[
        bool, typer.Option(help="Regenerate all previous colour swatches")
    ] = False,
):
    print, input = make_print("[green]\[generate-colours][/green]", True)

    session = create_session()
    if force_regen:
        q = select(Image)
    else:
        q = select(Image).where(Image.palette == None)  # noqa: E711
    results = session.scalars(q).all()
    print(f"Extracting colours for {len(results)} images.")
    try:
        for image in track(results):
            palette = extract_pallete(image.path, depth=num_images, quality=quality)
            image.palette = ",".join(map(rgb_to_hex, palette))
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()


@app.command()
def migrate(message: Annotated[str, typer.Argument(help="Description of the changes made")]):
    "Generate a migration script"
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, message, autogenerate=True)


@app.command()
def upgrade():
    "Upgrade the database"
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@app.command()
def reset(
    force: Annotated[
        bool,
        typer.Option(help="Make sure you're doing this on purpose..."),
    ],
):
    "Reset the database and parse all folders again."
    shutil.rmtree("migrations/versions")
    os.mkdir("migrations/versions")
    os.remove("db.sqlite")
    migrate("initial migration")
    upgrade()
    # setup()


def find_max(data, index):
    'Use this to find the appropriate "CR" for monsters'

    def get_maximum_element_from_json(element):
        if isinstance(element, int):
            return element
        else:
            return element[index]

    return max(map(get_maximum_element_from_json, data[index]))


def multiple_file_types(globber: Callable[[str], Iterator[pathlib.Path]], extensions: list[str]):
    "Glob multiple different extensions. Supply the pathlib.Path.glob or pathlib.Path.rglob to determine recursivity."
    return itertools.chain.from_iterable(globber(f"*.{extension}") for extension in extensions)


if __name__ == "__main__":
    app()
