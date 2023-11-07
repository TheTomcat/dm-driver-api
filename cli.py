from collections import defaultdict, namedtuple
import itertools
import json
import shutil
from sqlalchemy import delete, insert, select, update
import typer
from rich import print
from rich.progress import track, Progress
from typing import Annotated, Any, Generator
from api.models import Entity, Image, ImageType, Tag, image_tags
from core.session import create_session
import pathlib
from alembic.config import Config
from alembic import command
import uuid
import os

app = typer.Typer()

def make_print(prefix: str, verbose: bool):
    "Create a prefixed print and input function for scripts."
    def _print(*args, **kwargs):
        override = False
        if kwargs.get('override', False):
            override = True
            del kwargs['override']
        if verbose or override:
            if kwargs.get('np', False):
                del kwargs['np']
                print(*args, **kwargs) 
                return
            print(f'{prefix}', *args, **kwargs)
    def _input(prompt):
        print(f'{prefix}{prompt}', end='')
        return input()
        
    return _print, _input

@app.command()
def parse_directory(
    directory: Annotated[str, typer.Argument()], 
    extensions: Annotated[str, typer.Argument(help="Extensions to parse, comma separated")] = 'png',
    image_type: Annotated[ImageType, typer.Option(help="The type of image, to store in the database.")]='backdrop',
    force_reparse: Annotated[bool, typer.Option(help="If this is true, and an image with the same path and type is found in the database, it will be replaced.")]=False,
    verbose: Annotated[bool, typer.Option(help='Display detailed debugging')] = False,
    recursive: Annotated[bool, typer.Option(help='Search directories recursively')] = False,
):
    """Parse a directory for image files, and then store them in the database."""
    print, input = make_print('[red]\[parse-directory][/red] ', verbose)

    if force_reparse:
        i = input(":fire: Are you sure you want to continue? This may delete data. \[y/N]")
        if i.lower() != 'y':
            print('Exiting...')
            return
    path = pathlib.Path(directory)
    db_session = create_session()

    extensions = extensions.split(',')
    print(extensions, override=True)

    if recursive:
        iterable = multiple_file_types(path.rglob,extensions)
    else:
        iterable = multiple_file_types(path.glob,extensions)
    if not verbose:
        iterable = track([i for i in iterable], description="processing...")
    i=0
    for image_path in iterable:
        image = db_session.scalar(select(Image).where(Image.path==str(image_path) and Image.type==image_type))
        if image:
            print(f'Found image ([yellow]{image.type.name}[/yellow]) at [green]{image_path}[/green]', end='')
            if force_reparse:
                db_session.delete(image)
                print(f' - [red]Removing[/red]', np=True)
            else:
                print(f' - [yellow]Skipping[/yellow]', np=True)
                continue
        new_image = Image.create_from_local_file(image_path, type=image_type)
        db_session.add(new_image)
        i=i+1
        print(f'Adding image ([yellow]{new_image.type}[/yellow]) at [green]{image_path}[/green]')
    print(f"{i} items parsed", override=True)
    db_session.commit()

@app.command()
def parse_compendium(
    compendium_file: Annotated[str, typer.Argument(help="The file to parse")],
    verbose: Annotated[bool, typer.Option()] = False,
    process_images: Annotated[bool, typer.Option(help="Scan a folder for images that match the name of the monster, and then add them to the database")] = False,
    image_directory: Annotated[str, typer.Argument(help="The folder to scan. If not supplied, will attempt to guess the folder (using the usual structure of the 5e.tools codebase)")] = None 
):
    """Parse a 5e.tools file for entities to store in the database. This is horrible and globby but works for the moment. """
    print, input = make_print('[red]\[parse-compendium][/red] ', verbose)
    db_session = create_session()
    with open(compendium_file, "r") as f:
        data = json.load(f)
    

   
    if process_images and image_directory is None:
        process_images = True
        bestiaryimagepath = pathlib.Path(compendium_file).parent.parent.parent.joinpath(pathlib.Path('img\\bestiary'))
        if not bestiaryimagepath.is_dir():
            response = input('Unable to automatically detect image directory. Proceed anyway? [Y/n]')
            if response.lower() == 'n':
                return
    elif process_images and image_directory is not None:
        bestiaryimagepath = pathlib.Path(image_directory)
        if not bestiaryimagepath.is_dir():
            response = input(f'Supplied path {bestiaryimagepath} is not a valid directory. Proceed anyway? [Y/n]')
            if response.lower() == 'n':
                return

    i=0
    for monster in track(data["monster"], description="processing"):
        try:
            try: 
                cr = ((
                        monster["cr"]
                        if isinstance(monster["cr"], str)
                        else monster["cr"]["cr"]) if 'cr' in monster else ''
                    )
                hit_dice = monster["hp"]["formula"] if 'hp' in monster else ''
                ac = find_max(monster, "ac") if 'ac' in monster else 0
            except KeyError as e:
                # print(monster, ac, cr, hit_dice, override=True)
                continue
            m = Entity(
                name=monster["name"],
                hit_dice=hit_dice,
                ac=ac,
                cr=cr,
                initiative_modifier=monster.get("dex", 0),
                is_PC=False,
                source=monster["source"],
                source_page=monster["page"],
            )
            if process_images and monster.get('hasToken', False):
                
                datapath = bestiaryimagepath.joinpath(monster["source"].upper())
                if not datapath.is_dir():
                    continue
                
                file = list(datapath.glob(f'{monster.get("name")}*'))
                if file:
                    file = file[0]
                    image = Image.create_from_local_file(file, type=ImageType.character)
                    m.image=image
                    db_session.add(image)

        except Exception as e:
            print(monster)
            raise e
        print(f"Parsing {monster['name']}")
        db_session.add(m)
        i=i+1
    print(f"Parsed {i} elements.", override=True)
    db_session.commit()


@app.command()
def setup():
    "Perform a setup for my system"
    images = [
        # ( ImageType, Path, Recursive Search?, Extensions)
        ('backdrop', 'D:\\RPGs\\Backdrops', False, 'png'),
        ('character', 'D:\\RPGs\\Character Images', True, 'png,jpg,jpeg')
    ]

    compendia = [
        'D:\\RPGs\\5e.tools\\5etools-mirror-1.github.io-1.142.0\\data\\bestiary\\bestiary-mm.json',
        'D:\\RPGs\\5e.tools\\5etools-mirror-1.github.io-1.142.0\\data\\bestiary\\bestiary-mtf.json',
        'D:\\RPGs\\5e.tools\\5etools-mirror-1.github.io-1.142.0\\data\\bestiary\\bestiary-vgm.json',
        'D:\\RPGs\\5e.tools\\5etools-mirror-1.github.io-1.142.0\\data\\bestiary\\bestiary-ftd.json',
    ]

    for image_type, directory, recursive, extensions in images:
        parse_directory(directory, extensions, image_type, recursive=recursive)

    for compendium in compendia:
        parse_compendium(compendium, process_images=True)

@app.command()
def generate_tags():
    "Look in a folder full of images on my computer and try to guess appropriate tags for them."
    base_path = pathlib.Path('D:\\RPGs\\Character Images\\')
    db_session = create_session()
    
    images = db_session.scalars(select(Image).where(Image.path.ilike(f'%{base_path}%'))).all()
    tag_actions = defaultdict(list)
    for image in track(images):
        tags = os.path.normpath(pathlib.Path(image.path).relative_to(base_path)).split(os.sep)
        for tag in tags[:-1]:
            tag_actions[tag].append(image.id)
    
    for tagname, images in tag_actions.items():
        if tagname == "Default":
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
    convert_png: Annotated[bool, typer.Option(help="Convert images to png during the transfer. Not yet implemented.")] = False,
    use_subdir: Annotated[bool, typer.Option(help="Sort images based on their type (backdrop, character etc) into different folders.")] = False
    ):
    """Package the database and images to transfer them to another location. Warning, this could take a while"""
    print, input = make_print('[red]\[package][/red] ', True)
    output_directory = pathlib.Path(directory)
    if not output_directory.is_dir():
        print(f'Invalid output directory {directory}')
        return
    
    db_session = create_session()
    images = db_session.scalars(select(Image)).all()
    actions = []
    total_size = 0
    action_row = namedtuple('action_row',('image_id', 'old_path', 'new_path','size')) #  'new_name', 'extension', 'type', 
    for image in track(images, description="Parsing images..."):
        old_path = pathlib.Path(image.path)
        if not old_path.exists():
            print(f"Error parsing <Image id={image.id}>, not found at location {image.path}")
        size = os.path.getsize(image.path)
        new_name = uuid.uuid4()
        extension = image.path.split('.')[-1] #CONVERT_PNG: #if not convert_png else 'png'
        actions.append(action_row(
            image_id=image.id, 
            old_path=old_path, 
            new_path=output_directory.joinpath(f'{new_name}.{extension}'),
            size=size))
        total_size += size
    i = input(f"{len(actions)} files will now be migrated, total {total_size/1000000:.2f} MBi. Contine? \[y/N] ")
    if i.lower() != "y":
        print("Aborting...")
        return
    with Progress() as progress:
        num_files = progress.add_task("[red]Number of files...", total=len(actions))
        total_size = progress.add_task("[green]Total filesize...", total=total_size)
        for (image_id, old_path, new_path, size) in actions:
            shutil.copy(old_path, new_path)
            q = update(Image).where(Image.id == image_id).values(path=str(new_path))
            db_session.execute(q)
            progress.update(num_files, advance=1)
            progress.update(total_size, advance=size)
    db_session.commit()


@app.command()
def migrate(
    message: Annotated[str, typer.Argument(help="Description of the changes made")]
):
    "Generate a migration script"
    alembic_cfg = Config('alembic.ini')
    command.revision(alembic_cfg, message, autogenerate=True)

@app.command()
def upgrade():
    "Upgrade the database"
    alembic_cfg = Config('alembic.ini')
    command.upgrade(alembic_cfg, 'head')

def find_max(data, index):
    'Use this to find the appropriate "CR" for monsters'
    def get_maximum_element_from_json(element):
        if isinstance(element, int):
            return element
        else:
            return element[index]

    return max(map(get_maximum_element_from_json, data[index]))

def multiple_file_types(globber: Generator[pathlib.Path], extensions: list[str]):
    "Glob multiple different extensions. Supply the pathlib.Path.glob or pathlib.Path.rglob to determine recursivity."
    return itertools.chain.from_iterable(globber(f'*.{extension}') for extension in extensions)

if __name__ == "__main__":
    app()