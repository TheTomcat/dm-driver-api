#!/usr/local/bin/python3

import glob
from PIL import Image
from multiprocessing import Pool
from pathlib import Path
from functools import partial
from timeit import default_timer as timer


def generate_thumbnail(filename, zoom, outputdir="thumbnails"):
    try:
        # Load just once, then successively scale down
        start = timer()
        path = Path(filename)
        im = Image.open(filename)
        ar = im.size[1] / im.size[0]
        im.thumbnail((im.size[0] * zoom, im.size[1] * zoom))  # (535//2,150))
        im.save(path.parent.joinpath(outputdir).joinpath(path.name))
        end = timer()
        return path.name, end - start
    except Exception as e:
        return e


def parallel(files, zoom=0.25, outputdir="thumbnails", processes=8):
    start = timer()
    pool = Pool(processes)
    gen = partial(generate_thumbnail, zoom=zoom, outputdir=outputdir)
    results = pool.map(gen, files)
    end = timer()
    return end - start, results


def seq(files, zoom=0.25, outputdir="thumbnails"):
    start = timer()
    output = [
        generate_thumbnail(file, zoom=zoom, outputdir=outputdir) for file in files
    ]
    end = timer()
    return end - start, output


if __name__ == "__main__":
    files = glob.glob("D:\\RPGs\\Backdrops\\*.png")
