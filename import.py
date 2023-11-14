import itertools
import json
import os
import pathlib
import shutil
import uuid
from collections import defaultdict, namedtuple
from typing import Annotated, Callable, Iterator

import typer
from alembic import command
from alembic.config import Config
from rich.progress import Progress, track
from sqlalchemy import insert, select, update

from api.models import Combat, Entity, Image, Message, Participant, Tag, image_tags
from core.colour import extract_pallete
from core.session import create_session
from core.utils import rgb_to_hex


def add_players():
    "Add in my players"

    sess = create_session()
    image_map = (
        ("Aggie", "D:\\RPGs\\Campaigns\\2\\Aggie.png"),
        ("Fran", "D:\\RPGs\\Campaigns\\2\\Fran.png"),
        ("Sorsha", "D:\\RPGs\\Campaigns\\2\\Sorsha.png"),
        ("Gil", "D:\\RPGs\\Campaigns\\2\\Gilbert.png"),
    )
    players = []
    for name, image in image_map:
        i = Image.create_from_local_file(pathlib.Path(image), type="character")
        e = Entity(name=name, initiative_modifier=0, is_PC=True, image=i)
        players.append(e)
        sess.add_all([i, e])
    sess.commit()
    return players


def setup():
    players = add_players()

    load_messages("messages.json")

    load_tags("tags.json")

    build_dummy_data(players)

    generate_tags()


def load_tags(filename):
    "Load tags from my old version, loading from a json file format [[filename(with extension!), tagname], ...]"
    print, input = make_print("[red]\[load-tags][/red]        ", True)
    session = create_session()
    with open(filename, "r") as f:
        data = json.load(f)
    tags: set[str] = set()
    images: dict[str, Image] = {}
    for image, tag in data:
        tags.add(tag)
        images[image] = session.scalar(select(Image).where(Image.name == image[:-4]))

    tag_elements: dict[str, Tag] = {}
    for t in tags:
        tag_element = session.scalar(select(Tag).where(Tag.tag == t.lower()))
        if not tag_element:
            tag_element = Tag(tag=t.lower())
        tag_elements[t] = tag_element

    print(f"Found {len(tag_elements)} tags and {len(images)} images, with {len(data)} operations")
    session.add_all(tag_elements.values())

    for image, tag in data:
        images[image].tags.append(tag_elements[tag])

    session.commit()


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


@app.command()
def generate_tags():
    "Look in a folder full of images on my computer and try to guess appropriate tags for them, based on subfolders"
    print, input = make_print("[cyan]\[generate-tags][/cyan]    ", True)
    base_path = pathlib.Path("D:\\RPGs\\Character Images\\")
    db_session = create_session()

    images = db_session.scalars(select(Image).where(Image.path.ilike(f"%{base_path}%"))).all()
    tag_actions = defaultdict(list)
    for image in track(images):
        tags = os.path.normpath(pathlib.Path(image.path).relative_to(base_path)).split(os.sep)
        for tag in tags[:-1]:
            tag_actions[tag].append(image.id)
    print(
        f'Found {len(tag_actions)} tags: \[{", ".join([f"{tag}: {len(im)}" for tag, im in tag_actions.items()])}]'
    )
    for tagname, images in tag_actions.items():
        if tagname.lower() in [
            "default",  # Not sure why I made a folder called 'default'.
            "working wolder",
            "iacac",
        ]:
            continue
        tag = db_session.scalar(select(Tag).where(Tag.tag == tagname.lower()))
        if not tag:
            tag = Tag(tagname)
            db_session.add(tag)
            db_session.commit()
        for im_id in images:
            db_session.execute(insert(image_tags).values(image_id=im_id, tag_id=tag.id))
    db_session.commit()


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
):
    """Package the database and images to transfer them to another location. Warning, this could take a while"""
    print, input = make_print("[red]\[package][/red]        ", True)
    output_directory = pathlib.Path(directory)
    if not output_directory.is_dir():
        print(f"Invalid output directory {directory}")
        return

    db_session = create_session()
    images = db_session.scalars(select(Image)).all()
    actions = []
    total_size = 0
    action_row = namedtuple(
        "action_row", ("image_id", "old_path", "new_path", "size")
    )  #  'new_name', 'extension', 'type',
    for image in track(images, description="Parsing images..."):
        old_path = pathlib.Path(image.path)
        if not old_path.exists():
            print(f"Error parsing <Image id={image.id}>, not found at location {image.path}")
        size = os.path.getsize(image.path)
        new_name = uuid.uuid4()
        extension = image.path.split(".")[-1]  # CONVERT_PNG: #if not convert_png else 'png'
        actions.append(
            action_row(
                image_id=image.id,
                old_path=old_path,
                new_path=output_directory.joinpath(f"{new_name}.{extension}"),
                size=size,
            )
        )
        total_size += size
    i = input(
        f"{len(actions)} files will now be migrated, total {total_size/1000000:.2f} MBi. Contine? \[y/N] "
    )
    if i.lower() != "y":
        print("Aborting...")
        return
    count = 0
    with Progress() as progress:
        num_files = progress.add_task("[red]Number of files...", total=len(actions))
        total_size = progress.add_task("[green]Total filesize...", total=total_size)
        for image_id, old_path, new_path, size in actions:
            count += 1
            shutil.copy(old_path, new_path)
            q = update(Image).where(Image.id == image_id).values(path=str(new_path))
            db_session.execute(q)
            progress.update(num_files, advance=1)
            progress.update(total_size, advance=size)
    print(f'{count} images migrated, totalling {total_size/1000000:.2f} MBi."')
    db_session.commit()


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
    setup()


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
