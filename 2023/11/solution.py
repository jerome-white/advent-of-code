import sys
import logging
import functools as ft
import itertools as it
import collections as cl
from argparse import ArgumentParser
from multiprocessing import Pool

from scipy.spatial.distance import cityblock

Coordinate = cl.namedtuple('Coordinate', 'row, col')

class Universe:
    _empty = '.'
    _galaxy = '#'

    @ft.cached_property
    def dark_r(self):
        def dark():
            for (r, row) in enumerate(self.grid):
                if all(x == self._empty for x in row):
                    yield r

        return tuple(dark())

    @ft.cached_property
    def dark_c(self):
        def dark():
            (nrow, ncol) = (len(self.grid), len(self.grid[0]))
            for c in range(ncol):
                if all(self.grid[x][c] == self._empty for x in range(nrow)):
                    yield c

        return tuple(dark())

    def __init__(self, fp):
        self.grid = [ x.strip() for x in fp ]

    def __iter__(self):
        for (r, row) in enumerate(self.grid):
            for (c, cell) in enumerate(row):
                if cell == self._galaxy:
                    yield Coordinate(r, c)

#
#
#
def func(args):
    (u, v, dark, expansion) = args

    distance = cityblock(u, v)
    for (d, *e) in zip(dark, u, v):
        (l, r) = sorted(e)
        distance += sum(l < x < r for x in d) * expansion
    logging.warning('%s %s: %d', u, v, distance)

    return distance

def each(args, fp):
    if args.expansion is None:
        expansion = 2 if args.version == 1 else int(1e6)
    else:
        expansion = args.expansion
    expansion -= 1

    universe = Universe(fp)
    dark = (
        universe.dark_r,
        universe.dark_c,
    )

    for e in it.combinations(universe, r=2):
        yield (*e, dark, expansion)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--expansion', type=int)
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    with Pool(args.workers) as pool:
        distances = pool.imap_unordered(func, each(args, sys.stdin))
        print(sum(distances))
