import sys
import logging
import functools as ft
import itertools as it
import collections as cl
from argparse import ArgumentParser
from multiprocessing import Pool, Queue

import networkx as nx

Coordinate = cl.namedtuple('Coordinate', 'row, col')

class Grid:
    _galaxy = '#'

    @ft.cached_property
    def shape(self):
        return (len(self.grid), len(self.grid[0]))

    def __init__(self, fp):
        self.grid = [ x.strip() for x in fp ]

    def __iter__(self):
        for (r, row) in enumerate(self.grid):
            for (c, cell) in enumerate(row):
                if cell == self._galaxy:
                    yield Coordinate(r, c)

def func(incoming, outgoing, grid):
    G = nx.grid_2d_graph(*grid.shape)

    while True:
        (u, v) = incoming.get()
        plength = nx.shortest_path_length(G, source=u, target=v)
        logging.warning('%s -> %s: %d', u, v, plength)
        outgoing.put(plength)

def shortest_paths(args, fp):
    grid = Grid(fp)

    incoming = Queue()
    outgoing = Queue()
    initargs = (
        outgoing,
        incoming,
        grid,
    )

    with Pool(args.workers, func, initargs):
        jobs = 0
        for e in it.combinations(grid, r=2):
            outgoing.put(e)
            jobs += 1

        for _ in range(jobs):
            result = incoming.get()
            yield result

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    print(sum(shortest_paths(args, sys.stdin)))
